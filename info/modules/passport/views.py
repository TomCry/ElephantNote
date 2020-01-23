from datetime import datetime
import random
import re
from flask import request, abort, current_app, make_response, jsonify, session

from info import redis_store, constants, db
from info.libs.yuntongxun.sms import CCP
from info.models import User
from info.utils.response_code import RET
from . import passport_blu
from info.utils.captcha.captcha import captcha


@passport_blu.route('/logout')
def logout():
    """
    退出登录
    :return:
    """
    # pop有一个返回值，如果一处的key不存在就返回none
    session.pop('user_id', None)
    session.pop('mobile', None)
    session.pop('nick_name', None)

    return jsonify(errno=RET.OK, errmsg="退出成功")


@passport_blu.route('/login', methods=["POST"])
def login():
    """
    1.获取参数
    2.校验参数
    3.校验密码是否正确
    4.保存用户登录状态
    5.返回响应
    :return:
    """
    params_dict = request.json
    mobile = params_dict.get("mobile")
    password = params_dict.get("password")

    # 2 校验参数
    if not all([mobile, password]):
        return jsonify(errno=RET.PARAMERR, errmsg="参数错误")

    # 校验手机号是否正确
    if not re.match('1[25678]\\d{9}', mobile):
        return jsonify(errno=RET.PARAMERR, errmsg="手机号格式不正确")

    # 3. 校验密码是否正确
    # 3-1 查询当前是否有该用户
    try:
        user = User.query.filter(User.mobile == mobile).first()
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.DB, errmsg="数据查询错误")

    if not user:
        return jsonify(errno=RET.NODATA, errmsg="用户不存在")

    # 4 校验密码
    if not user.check_password(password):
        return jsonify(errno=RET.PWDERR, errmsg="密码错误")

    # 5 保存用户状态
    session["user_id"] = user.id
    session["mobile"] = user.mobile
    session["nick_name"] = user.nick_name

    # 设置当前用户最后一次登录时间
    user.last_login = datetime.now()

    # 如果在视图函数中，对模型身上的属性有修改，需要commit到数据库保存
    # 但是其实不用写db.session.commit()，前提是对SQLAlchemy有相关配置

    # 修改数据库
    try:
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(e)

    # 6 响应
    return jsonify(errno=RET.OK, errmsg="登录成功")



@passport_blu.route('/register', methods=["POST"])
def register():
    """
    注册的逻辑
    1. 获取参数
    2. 校验参数
    3. 取到服务器保存的真实的短信验证码内容
    4. 校验用户输入的短信验证码内容和真实验证码内容
    5. 一致：初始化User模型，并且赋值
    6. 将user模型添加到数据库
    7. 返回响应
    :return:
    """
    # 1.获取参数
    param_dict = request.json
    mobile = param_dict.get("mobile")
    smscode = param_dict.get("smscode")
    password = param_dict.get("password")

    # 2.校验参数
    if not all([mobile, smscode, password]):
        return jsonify(errno=RET.PARAMERR, errmsg="参数")

    # 校验手机号是否正确
    if not re.match('1[35678]\\d{9}', mobile):
        return jsonify(errno=RET.PARAMERR, errmsg="手机号格式不正确")

    # 3. 取真实验证码
    try:
        real_sms_code = redis_store.get("SMS_" + mobile)
        print(real_sms_code)
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.DBERR, errmsg="数据查询失败")

    if not real_sms_code:
        return jsonify(errn=RET.NODATA, errmsg="验证码已过期")

    # 4. 校验用户输入的短信验证码内容和真实验证码是否一致
    if real_sms_code != smscode:
        return jsonify(errno=RET.DATAERR, errmsg="验证码输入错误")

    # 5. User ，赋值属性
    user = User()
    user.mobile = mobile
    user.nick_name = mobile
    # 记录用户最后一次登录时间
    user.last_login = datetime.now()
    # TODO 对密码做处理
    user.password = password
    # 6. user添加数据库
    try:
        db.session.add(user)
        db.session.commit()
    except Exception as e:
        current_app.logger.error(e)
        db.session.rollback()
        return jsonify(errno=RET.DBERR, errmsg="数据保存失败")

    # 往session中保存数据表示当前已登录
    session["user_id"] = user.id
    session["mobile"] = user.mobile
    session["nick_name"] = user.nick_name


    # 7.返回响应
    return jsonify(errno=RET.OK, errmsg="注册成功")




@passport_blu.route('/sms_code', methods=["POST"])
def send_sms_code():
    """
    发送短息的逻辑
    1. 发送短信，获取手机号，图片验证码内容，图片验证码编号
    2. 校验参数（参数是否符合规则，判断是否有值）
    3. 先从redis中取出真实的验证码内容，与用户的验证码内容进行对比
    4. 如果对比不一致，那么返回验证码输入错误
    5. 如果一致，生成验证码内容
    6. 发送短信验证吗
    7. 告知发送结果
    :return:
    """
    params_dict = request.json

    mobile = params_dict.get('mobile')
    image_code = params_dict.get("image_code")
    image_code_id = params_dict.get("image_code_id")
    # return jsonify(errno=RET.OK, errmsg="发送成功")
    # 2. 校验参数
    if not all([mobile, image_code, image_code_id]):
        return jsonify(errno=RET.PARAMERR, errmsg="参数有误")
    #
    if not re.match('1[35678]\\d{9}', mobile):
        return jsonify(errno=RET.PARAMERR, errmsg="手机号格式不正确")

    # 3. 从redis中取验证码内容
    try:
        real_image_code = redis_store.get("ImageCodeId_" + image_code_id)
        print(real_image_code)
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.DBERR, errmsg="数据查询失败")

    if not real_image_code:
        return jsonify(errno=RET.NODATA, errmsg="图片验证码已过期")

    # 4. 对比验证码
    if real_image_code.upper() != image_code.upper():
        return jsonify(errno=RET.DATAERR, errmsg="验证码输入错误")

    # 5. 如果一致，生成短信验证码内容         # 随机数字，保证数字长度6位，不够在前面补上0
    sms_code_str ="%06d" % random.randint(0, 999999)
    print(sms_code_str)
    current_app.logger.debug("短信验证码内容是: %s" % sms_code_str)
    # 6. 发送短信验证码
    # result = CCP().send_template_sms(mobile, [sms_code_str, constants.SMS_CODE_REDIS_EXPIRES / 5], "1")
    # if result != 0:
    #     # 代表发送不成功
    #     return jsonify(errno=RET.THIRDERR, errmsg="发送短信失败")
    # 保存验证码内容到redis
    try:
        redis_store.set("SMS_" + mobile, sms_code_str, constants.SMS_CODE_REDIS_EXPIRES)
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.DBERR, errmsg="数据保存失败")
     # 7 告知发送结果
    return jsonify(errno=RET.OK, errmsg="发送成功")


@passport_blu.route('/image_code')
def get_image_code():
    '''生成图片验证码并返回'''
    # 1. 取到参数 args 取url中？后面的参数
    image_code_id = request.args.get('imageCodeId', None)
    # 2. 判断参数是否有值
    if not image_code_id:
        return abort(403)
    # 3. 生成图片验证码
    name, text, image = captcha.generate_captcha()
    print(text)
    current_app.logger.debug("图片验证码内容是：%s" % text)
    # 4. 保存图片验证码文字内容到redis
    try:
        redis_store.set("ImageCodeId_" + image_code_id, text, constants.IMAGE_CODE_REDIS_EXPIRES)
    except Exception as e:
        current_app.logger.error(e)
        abort(500)
    # 5. 返回验证码图片
    # 设置content-type, 以便浏览器识别减少不便的报错
    response = make_response(image)
    response.headers['Content-Type'] = "image/jpg"
    return response