from redis import StrictRedis


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