from flask import Blueprint, session, redirect, url_for, request

# 创建蓝图对象
admin_blu = Blueprint("admin", __name__)

from . import views

@admin_blu.before_request
def check_admin():
    # 如果不是管理直接跳转到主页
    is_admin = session.get("is_admin", False)
    if not is_admin and not request.url.endswith(url_for('admin.login')) :
        return redirect('/')