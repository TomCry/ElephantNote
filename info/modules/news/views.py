from flask import render_template

from info.modules.news import news_blu


#127.0.0.1:9999/news/2
@news_blu('/<int:news_id>')
def news_detail(news_id):

    """
    新闻详情
    :param news_id:
    :return:
    """

    return render_template("news/detail.html")
