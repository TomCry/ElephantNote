from flask import render_template, g, redirect, request, jsonify, current_app

from info import constants, db
from info.models import Category, News
from info.modules.profile import profile_blu
from info.utils.common import user_login_data
from info.utils.image_store import storage
from info.utils.response_code import RET


@profile_blu.route('/news_list')
@user_login_data
def user_news_list():
    user = g.user
    page = request.args.get("p",1)

    news_list = []
    current_page = 1
    total_page = 1
    try:
        pagination = News.query.filter(News.user_id==user.id).paginate(page, constants.USER_COLLECTION_MAX_NEWS,False)
        news_list = pagination.items
        current_page = pagination.page
        total_page = pagination.pages
    except Exception as e:
        current_app.logger.error(e)

    news_list_li = []
    for news in news_list:
        news_list_li.append(news.to_review_dict())

    data = {
        "news_list": news_list_li,
        "current_page": current_page,
        "total_page": total_page
    }

    return render_template('news/user_news_list.html',data=data)


@profile_blu.route('/news_release', methods=["GET", "POST"])
@user_login_data
def news_release():


    if request.method == "GET":
        # 加载新闻分类数据
        try:
            categories = Category.query.all()
        except Exception as e:
            current_app.logger.error(e)

        category_dict_li = []
        for category in categories:
            category_dict_li.append(category.to_dict())

        # 移除最新分类
        category_dict_li.pop(0)

        return render_template('news/user_news_release.html', data={"categories": category_dict_li})

    user = g.user

    # 1. 获取要提交的数据
    title = request.form.get("title")
    source = "个人发布"
    digest = request.form.get("digest")
    content = request.form.get("content")
    index_image = request.files.get("index_image")
    category_id = request.form.get("category_id")
    # 1.1 判断数据是否有值
    if not all([title, source, digest, content, index_image, category_id]):
        return jsonify(errno=RET.PARAMERR, errmsg="参数有误")

    # 校验参数
    try:
        category_id = int(category_id)
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.PARAMERR, errmsg="参数有误")

    # 取到图片，将图片上传至七牛云
    try:
        index_image_data = index_image.read()
        # 上传至七牛云
        key = storage(index_image_data)
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.PARAMERR, errmsg="参数有误")


    news = News()
    news.title = title
    news.digest = digest
    news.source = source
    news.content = content
    news.index_image_url = constants.QINIU_DOMIN_PREFIX + key
    news.category_id = category_id
    news.user_id = user.id
    # 1代表待审核状态
    news.status = 1

    try:
        db.session.add(news)
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        return jsonify(errno=RET.DBERR, errmsg="数据保存失败")

    return jsonify(errno=RET.OK, errsmg="OK")

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