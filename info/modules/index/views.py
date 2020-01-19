from flask import render_template

from info import redis_store
from . import index_blu


@index_blu.route('/')
def index():
    # # redis保存值
    # redis_store.set("name","notation")

    return render_template('news/index.html')
