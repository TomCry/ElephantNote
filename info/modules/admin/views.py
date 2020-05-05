import time
from datetime import datetime

from flask import render_template, request, current_app, session, redirect, url_for, g

from info.models import User
from info.modules.admin import admin_blu
from info.utils.common import user_login_data


@admin_blu.route('/user_count')
def user_count():
    total_count = 0
    try:
        total_count = User.query.filter(User.is_admin == False).count()
    except Exception as e:
        current_app.logger.error(e)
    # 月新增数大于当月1号0分0秒
    month_count = 0
    t = time.localtime()
    print(t)
    begin_mon = datetime.strptime(('%s-%02d-01' % (t.tm_year,t.tm_mon)), "%Y-%m-%d")
    print(begin_mon)

    try:
        month_count = User.query.filter(User.is_admin == False, User.create_time > begin_mon).count()
    except Exception as e:
        current_app.logger.error(e)


    day_count = 0
    t = time.localtime()
    print(t)
    begin_day = datetime.strptime(('%s-%02d-%02d' % (t.tm_year, t.tm_mon, t.tm_mday)), "%Y-%m-%d")
    print(begin_mon)
    try:
        day_count = User.query.filter(User.is_admin == False, User.create_time > begin_day).count()
    except Exception as e:
        current_app.logger.error(e)

    data = {
        "total_count": total_count,
        "month_count": month_count,
        "day_count": day_count,
    }
    return render_template('admin/user_count.html', data=data)


@admin_blu.route('/index')
@user_login_data
def index():
    user = g.user
    return render_template('admin/index.html', user=user.to_dict())


@admin_blu.route('/login', methods=["GET", "POST"])
def login():
    if request.method == "GET":
        # 判断当前是否有登录，如果有登录直接重定向到管理员后台主页
        user_id = session.get("user_id", None)
        is_admin = session.get("is_admin", False)

        if user_id and is_admin:
            return redirect(url_for("admin.index"))

        return render_template('admin/login.html')

    # 取到登录的参数
    username = request.form.get("username")
    password = request.form.get("password")

    # 判断参数
    if not all([username, password]):
        return render_template('admin/login.html', errmsg="参数错误")

    # 查询当前用户
    try:
        user = User.query.filter(User.mobile == username, User.is_admin == True).first()
    except Exception as e:
        current_app.logger.error(e)
        return render_template('admin/login.html', errmsg="参数错误")

    if not user:
        return render_template('admin/login.html', errmsg="未查询到用户信息")

    # 校验密码
    if not user.check_password(password):
        return render_template('admin/login.html', errmsg="用户名或者密码错误")

    # 保存用户的登录信息
    session["user_id"] = user.id
    session["mobile"] = user.mobile
    session["nick_name"] = user.nick_name
    session["is_admin"] = user.is_admin

    # 跳转到管理后台首页
    return redirect(url_for('admin.index'))
