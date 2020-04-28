from flask import render_template, current_app, session, abort, g, request, jsonify

from info import constants, db
from info.models import News, User, Comment
from info.modules.news import news_blu


# 127.0.0.1:9999/news/2
from info.utils.common import user_login_data
from info.utils.response_code import RET


@news_blu.route('/news_comment', method=["POST"])
@user_login_data
def comment_news():
    """
    评论新闻或者回复某条新闻下指定的评论
    :return:
    """
    # 1.获取用户
    user = g.user

    if not user:
        return jsonify(errno=RET.SESSIONERR, errmsg="用户未登录")
    # 2.获取请求参数
    news_id = request.json.get("news_id")
    content = request.json.get("content")
    parent_id = request.json.get("parent_id")

    # 3.判断参数
    if not all([news_id, content]):
        return jsonify(errno=RET.PARAMERR, errmsg="参数错误")

    try:
        news_id = int(news_id)
        if parent_id:
            parent_id = int(parent_id)
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.PARAMERR, errmsg="参数错误")

    # 查询新闻，并判断新闻是否存在

    try:
        news = News.query.get(news_id)
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.DBERR, errmsg="数据查询错误")

    if not news:
        return jsonify(errno=RET.NODATA, errmsg="未查询到新闻数据")

    # 4.初始化评论模型，并且赋值
    comment = Comment()
    comment.user_id = user.id
    comment.news_id = news.id
    comment.content = content
    if parent_id:
        comment.parent_id = parent_id

    # 5.添加到数据库
    # commit的原因，因为需要在commit之后才会生成id，我们需要返回comment_id
    try:
        db.session.add(comment)
        db.session.commit()
    except Exception as e:
        current_app.logger.error(e)
        db.session.rollback()

    return jsonify(errno=RET.OK, errmsg="OK", comment=comment.to_dict())


@news_blu.route('/news_collect',methods=["POST"])
@user_login_data
def collect_news():
    """
    收藏新闻
    1.接收参数
    2.判断参数
    :return:
    """
    user = g.user
    if not user:
        return jsonify(errno=RET.SESSIONERR, errmsg="用户未登录")

    news_id = request.json.get("news_id")
    action = request.json.get("action")

    if not all([news_id, action]):
        return jsonify(errno=RET.PARAMERR,errmsg="参数错误")

    if action not in ["collect","cancel_collect"]:
        return jsonify(errno=RET.PARAMERR,errmsg="参数错误")


    try:
        news_id = int(news_id)
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.PARAMERR, errmsg="参数错误")

    # 3.查询新闻，并判断新闻是否存在
    news = None

    try:
        news = News.query.get(news_id)
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.DBERR, errmsg="数据查询错误")

    if not news:
        return jsonify(errno=RET.NODATA, errmsg="未查询到新闻数据")

    if action == "cancel_collect":
        # 取消收藏
        if news in user.collection_news:
            user.collection_news.remove(news)
    else:
        # 4. 进行收藏
        if news not in user.collection_news:
            user.collection_news.append(news)


    return jsonify(errno=RET.OK, errmsg="操作成功")




@news_blu.route('/<int:news_id>')
@user_login_data
def news_detail(news_id):
    """
    新闻详情
    :param news_id:
    :return:
    """

    # 查询用户登录信息
    # user_id = session.get("user_id", None)
    # user = None
    # if user_id:
    #     try:
    #         user = User.query.get(user_id)
    #     except Exception as e:
    #         current_app.logger.error(e)

    user = g.user
    news_list = []
    # 右侧新闻排行逻辑
    try:
        news_list = News.query.order_by(News.clicks.desc()).limit(constants.CLICK_RANK_MAX_NEWS)
    except Exception as e:
        current_app.logger.error(e)

    news_dict_list = []
    # 遍历对象列表，将对象的字典添加到字典列表中
    for news in news_list:
        news_dict_list.append(news.to_basic_dict())

    # 查询新闻数据
    news = None
    try:
        news = News.query.get(news_id)
    except Exception as e:
        current_app.logger.error(e)

    if not News:
        # 报404错误，404错误统一显示页面后续处理
        abort(404)

    # 更新新闻点击次数
    news.clicks += 1
    is_collected = False

    # 如果用户已登录：
    # 判断用户是否收藏当前新闻，如果收藏：
    # is_collected = True

    if user:
        # 判断用户是否收藏新闻
        # collection_news不用加all()，sqlalchemy会自动进行加载
        if news in user.collection_news:
            is_collected = True


    data = {
        "user": user.to_dict() if user else None,
        "news_dict_li": news_dict_list,
        "news": news.to_dict(),
        "is_collected": is_collected
    }

    return render_template("news/detail.html",data=data)
