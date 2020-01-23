from flask import render_template, current_app, session

from info import redis_store
from info.models import User, News
from . import index_blu


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
        news_list = News.query.order_by(News.clicks.desc()).limit(6)
    except Exception as e:
        current_app.logger.error(e)

    news_dict_list = []
    # 遍历对象列表，将对象的字典添加到字典列表中
    for news in news_list:
        news_dict_list.append(news.to_basic_dict())

    data = {
        "user": user.to_dict() if user else None,
        "news_dict_list": news_dict_list
    }




    return render_template('news/index.html', data=data)


# 在打开网页的时候，浏览器会请求根路径+favicon.icon小图标
@index_blu.route('/favicon.ico')
def favicon():
    return current_app.send_static_file('news/favicon.ico')
