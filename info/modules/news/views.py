from flask import render_template, current_app, session, abort, g

from info import constants
from info.models import News, User
from info.modules.news import news_blu


# 127.0.0.1:9999/news/2
from info.utils.common import user_login_data


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

    data = {
        "user": user.to_dict() if user else None,
        "news_dict_li": news_dict_list,
        "news": news.to_dict()
    }

    return render_template("news/detail.html",data=data)
