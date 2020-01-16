from flask import Flask
from flask_session import Session
from flask_sqlalchemy import SQLAlchemy
from flask_wtf import CSRFProtect
from redis import StrictRedis

from config import config

# 在flask很多扩展里面都可以先初始化，然后init_app方法初始化
db = SQLAlchemy()

def create_app(config_name):
    app = Flask(__name__)
    # 加载配置
    app.config.from_object(config[config_name])
    # 通过app初始化
    db.init_app(app)
    redis_store = StrictRedis(host=config[config_name].REDIS_HOST,port=config[config_name].REDIS_PORT)
    # 开启csrf保护,只做服务器验证功能
    CSRFProtect(app)
    # 设置session保存指定位置
    Session(app)

    return app