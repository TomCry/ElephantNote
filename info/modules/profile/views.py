from flask import render_template, g, redirect, request, jsonify, current_app

from info import constants
from info.modules.profile import profile_blu
from info.utils.common import user_login_data
from info.utils.image_store import storage
from info.utils.response_code import RET


@profile_blu.route('/pic_info', methods=["GET","POST"])
@user_login_data
def pic_info():

    user = g.user
    if request.method == "GET":
        return render_template('news/user_pic_info.html', data={"user": user.to_dict()})

    # TODO 如果是POST表示修改头像
    # 1. 获取参数图片
    try:
        file = request.files.get("avatar").read()
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.PARAMERR, errmsg="参数错误")
    # 2.上传头像
    try:
        key = storage(file)
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.THIRDERR, errmsg="上传头像失败")

    # 3.保存头像地址
    user.avatar_url = key

    return jsonify(errno=RET.OK, errmsg="OK", avatar_url=constants.QINIU_DOMIN_PREFIX+key)




@profile_blu.route('/base_info', methods=["GET", "POST"])
@user_login_data
def base_info():
    user = g.user
    if request.method == "GET":
        return render_template('news/user_base_info.html', data={"user": user.to_dict()})
    # 修改用户数据，不同的请求方式做不同的事情
    # 1.取到传入的参数
    nick_name = request.json.get("nick_name")
    signature = request.json.get("signature")
    gender = request.json.get("gender")

    # 2.校验参数
    if not all([nick_name, signature, gender]):
        return jsonify(errno=RET.PARAMERR, errmsg="参数错误")

    if gender not in ("WOMAN", "MAN"):
        return jsonify(errno=RET.PARAMERR, errmsg="参数错误")

    user.signature = signature
    user.nick_name = nick_name
    user.gender = gender

    return jsonify(errno=RET.OK, errmsg="OK")



@profile_blu.route('/info')
@user_login_data
def user_info():
    user = g.user

    if not user:
        return redirect("/")
    data = {
        "user":user.to_dict(),
    }
    return render_template('news/user.html',data=data)