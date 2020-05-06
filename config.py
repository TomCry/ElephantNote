import logging
from redis import StrictRedis


class Config(object):
    """项目的配置"""
    DEBUG = True

    SECRET_KEY = 'sdfsdfsdf'
    # 为Mysql添加配置
    SQLALCHEMY_DATABASE_URI="mysql+pymysql://root:enzyme0313@127.0.0.1:3306/elephant"
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    # 在请求结束的时候，如果指定此配置为True，那么SQLALchemy 会自动执行一次 db.session.commit()
    # 04-09
    SQLALCHEMY_COMMIT_ON_TEARDOWN = True

    # Redis配置
    REDIS_HOST = '172.16.211.146'
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

    # 设置日志等级
    LOG_LEVEL = logging.DEBUG


class DevConfig(Config):
    """开发环境下配置"""
    DEBUG = True

class ProConfig(Config):
    """生产环境配置"""
    DEBUG = False
    LOG_LEVEL = logging.WARNING

class TestingConfig(Config):
    """单元测试环境下的配置"""
    DEBUG = True
    TESTING = True

config = {
    "dev": DevConfig,
    "production": ProConfig,
    "testing": TestingConfig
}