import logging

from flask import session, current_app
from flask_script import Manager
from flask_migrate import Migrate, MigrateCommand

from info import create_app, db, models

# manage.py是程序启动的入口，只关心启动的相关参数以及内容，不关心具体业务逻辑

# 通过指定的配置名字创建对应配置的app
from info.models import User

app = create_app('dev')

manager = Manager(app)
#将app与db关联
Migrate(app, db)
#将迁移命令添加到manager中
manager.add_command('db', MigrateCommand)


@manager.option('-n', '-name', dest="name")
@manager.option('-p', '-password', dest='password')
def createsuperuser(name, password):
    if not all([name, password]):
        print("参数不足")

    user = User()
    user.nick_name = name
    user.mobile = name
    user.password = password
    user.is_admin = True

    try:
        db.session.add(user)
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        print(e)

    print("添加成功")



if __name__ == '__main__':
    manager.run()