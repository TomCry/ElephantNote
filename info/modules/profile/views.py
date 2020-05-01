from flask import render_template, g, redirect, request, jsonify, current_app

from info import constants
from info.modules.profile import profile_blu
from info.utils.common import user_login_data
from info.utils.image_store import storage
from info.utils.response_code import RET


@profile_blu.route('/collection')
@user_login_data
def user_collection():

    # 1.获取参数
    page = request.args.get("p", 1)
    # 2.判断参数
    try:
        page = int(page)
    except Exception as e:
        current_app.logger.error(e)
        page = 1

    # 3. 查询用户指定页数的收藏的新闻
    user = g.user

    try:
        paginate = user.collection_news.paginate(page, constants.USER_COLLECTION_MAX_NEWS, False)
        current_page = paginate.page
        total_page = paginate.pages
        news_list = paginate.items
    except Exception as e:
        current_app.logger.error(e)


    news_dict_li = []
    for news in news_list:
        news_dict_li.append(news.to_basic_dict())

    data = {
        "total_page": total_page,
        "current_page": current_page,
        "collections": news_dict_li
    }


    return render_template('news/user_collection.html', data=data)


@profile_blu.route('/pass_info', methods=["GET","POST"])
@user_login_data
def pass_info():
    if request.method == "GET":

        return render_template('news/user_pass_info.html')

    # 1.获取参数
    new_password = request.json.get("new_password")
    old_password = request.json.get("old_password")

    # 2.校验参数
    if not all([new_password, old_password]):
        return jsonify(errno=RET.PARAMERR, errmsg="参数错误")

    # 3.判断旧密码
    user = g.user
    if not user.check_password(old_password):
        return jsonify(errno=RET.PWDERR, errmsg="旧密码输入错误")

    # 4.设置新密码
    user.password = new_password

    return jsonify(errno=RET.OK, errmsg="密码设置成功")

@profile_blu.route('/pic_info', methods=["GET","POST"])
@user_login_data
def pic_info():

    user = g.user
    if request.method == "GET":
        return render_template('news/user_pic_info.html', data={"user": user.to_dict()})

    # TODO 如果是POST表示修改头像
    # 1. 获取参数图片
    try:
        file = request.files.get("avatar").read()
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.PARAMERR, errmsg="参数错误")
    # 2.上传头像
    try:
        key = storage(file)
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.THIRDERR, errmsg="上传头像失败")

    # 3.保存头像地址
    user.avatar_url = key
    data = {
        "avatar_url": constants.QINIU_DOMIN_PREFIX,
    }

    return jsonify(errno=RET.OK, errmsg="OK", data=data)




@profile_blu.route('/base_info', methods=["GET", "POST"])
@user_login_data
def base_info():
    user = g.user
    if request.method == "GET":
        return render_template('news/user_base_info.html', data={"user": user.to_dict()})
    # 修改用户数据，不同的请求方式做不同的事情
    # 1.取到传入的参数
    nick_name = request.json.get("nick_name")
    signature = request.json.get("signature")
    gender = request.json.get("gender")

    # 2.校验参数
    if not all([nick_name, signature, gender]):
        return jsonify(errno=RET.PARAMERR, errmsg="参数错误")

    if gender not in ("WOMAN", "MAN"):
        return jsonify(errno=RET.PARAMERR, errmsg="参数错误")

    user.signature = signature
    user.nick_name = nick_name
    user.gender = gender

    return jsonify(errno=RET.OK, errmsg="OK")



@profile_blu.route('/info')
@user_login_data
def user_info():
    user = g.user

    if not user:
        return redirect("/")
    data = {
        "user":user.to_dict(),
    }
    return render_template('news/user.html',data=data)