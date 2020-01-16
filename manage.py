from flask import Flask, session
from flask_sqlalchemy import SQLAlchemy
from flask_wtf import CSRFProtect
from redis import StrictRedis
# 可以用来指定session保存位置
from flask_session import Session
from flask_script import Manager

class Config(object):
    """项目的配置"""
    DEBUG = True

    SECRET_KEY = 'sdfsdfsdf'
    # 为Mysql添加配置
    SQLALCHEMY_DATABASE_URI="mysql+pymysql://root:enzyme0313@127.0.0.1:3306/elephant"
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # Redis配置
    REDIS_HOST = '172.16.211.129'
    REDIS_PORT = 6379

    # Session保存配置
    SESSION_TYPE = 'redis'
    # 是否SIGNER
    SESSION_USER_SIGNER = False

    SESSION_PERMANENT = False
    # 设置过期时间
    PERMANENT_SESSION_LIFETIME = 86400 * 2
    # 指定session保存到redis
    SESSION_REDIS = StrictRedis(host=REDIS_HOST, port=REDIS_PORT)

app = Flask(__name__)
# 加载配置
app.config.from_object(Config)

db = SQLAlchemy(app)

redis_store = StrictRedis(host=Config.REDIS_HOST,port=Config.REDIS_PORT)
# 开启csrf保护,只做服务器验证功能
CSRFProtect(app)
# 设置session保存指定位置
Session(app)

manager = Manager(app)

@app.route('/')
def index():
    session['name'] = 'itheima'
    return "index"


if __name__ == '__main__':
    manager.run()