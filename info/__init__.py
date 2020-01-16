from flask import Flask
from flask_session import Session
from flask_sqlalchemy import SQLAlchemy
from flask_wtf import CSRFProtect
from redis import StrictRedis

from config import config

app = Flask(__name__)
# 加载配置
app.config.from_object(config['dev'])

db = SQLAlchemy(app)

redis_store = StrictRedis(host=config['dev'].REDIS_HOST,port=config['dev'].REDIS_PORT)
# 开启csrf保护,只做服务器验证功能
CSRFProtect(app)
# 设置session保存指定位置
Session(app)