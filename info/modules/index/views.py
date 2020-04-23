from flask import render_template, current_app, session, request, jsonify

from info import redis_store, constants
from info.models import User, News, Category
from info.utils.response_code import RET
from . import index_blu

@index_blu.route('/news_list')
def news_list():
    """
    获取首页新闻数据
    :return:
    """
    # 1. 获取参数
    cid = request.args.get("cid", "1")
    page = request.args.get("page", "1")
    per_page = request.args.get("per_page", "10")

    # 2. 校验参数
    try:
        cid = int(cid)
        page = int(page)
        per_page = int(per_page)
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.PARAMERR, errmsg="参数错误")

    filters = []
    if cid != 1:
        # 需要添加条件
        filters.append(News.category_id == cid)
    # 3. 查询数据
    try:
        paginate = News.query.filter(*filters).order_by(News.create_time.desc()).paginate(page, per_page, False)
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.DBERR, errmsg="数据查询错误")

    # 取到当前页的数据
    news_model_list = paginate.items  # 模型对象列表
    total_page = paginate.pages
    current_page = paginate.page

    news_dict_list = []
    print(news_model_list)

    for news in news_model_list:
        news_dict_list.append(news.to_basic_dict())


    data = {
        "total_page": total_page,
        "current_page": current_page,
        "news_dict_list": news_dict_list
    }

    return jsonify(errno=RET.OK, errmsg="OK", data=data)

@index_blu.route('/')
def index():
    # # redis保存值
    # redis_store.set("name","notation")
    """
    1. 如果用户已经登录，将当前用户的数据传入模板，进行显示
    2.
    :return:
    """
    # 1
    user_id = session.get("user_id", None)
    user = None
    if user_id:
        try:
            user = User.query.get(user_id)
        except Exception as e:
            current_app.logger.error(e)

    # 右侧新闻排行逻辑
    try:
        news_list = News.query.order_by(News.clicks.desc()).limit(constants.CLICK_RANK_MAX_NEWS)
    except Exception as e:
        current_app.logger.error(e)

    news_dict_list = []
    # 遍历对象列表，将对象的字典添加到字典列表中
    for news in news_list:
        news_dict_list.append(news.to_basic_dict())


    # 查询分类数据， 通过模板渲染
    categories = Category.query.all()
    category_li = []
    for category in categories:
        category_li.append(category.to_dict())

    data = {
        "user": user.to_dict() if user else None,
        "news_dict_list": news_dict_list,
        "category_li": category_li
    }




    return render_template('news/index.html', data=data)


# 在打开网页的时候，浏览器会请求根路径+favicon.icon小图标
@index_blu.route('/favicon.ico')
def favicon():
    return current_app.send_static_file('news/favicon.ico')
