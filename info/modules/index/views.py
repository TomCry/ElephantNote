from flask import render_template, current_app

from info import redis_store
from . import index_blu


@index_blu.route('/')
def index():
    # # redis保存值
    # redis_store.set("name","notation")

    return render_template('news/index.html')


# 在打开网页的时候，浏览器会请求根路径+favicon.icon小图标
@index_blu.route('/favicon.ico')
def favicon():
    return current_app.send_static_file('news/favicon.ico')
