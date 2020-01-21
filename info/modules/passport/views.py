import random
import re
from flask import request, abort, current_app, make_response, jsonify

from info import redis_store, constants
from info.libs.yuntongxun.sms import CCP
from info.utils.response_code import RET
from . import passport_blu
from info.utils.captcha.captcha import captcha


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
    return jsonify(errno=RET.OK, errmsg="发送成功")
    # 2. 校验参数
    if not all([mobile, image_code, image_code_id]):
        return jsonify(errno=RET.PARAMERR, errmsg="参数有误")
    #
    if not re.match('1[35678]\\d{9}'):
        return jsonify(errno=RET.PARAMERR, errmsg="手机号格式不正确")

    # 3. 从redis中取验证码内容
    try:
        real_image_code = redis_store.get("ImageColdId_" + image_code_id)
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
    current_app.looger.debug("短信验证码内容是: %s" % sms_code_str)
    # 6. 发送短信验证码
    result = CCP().send_template_sms(mobile, [sms_code_str, constants.SMS_CODE_REDIS_EXPIRES / 5], "1")
    if result != 0:
        # 代表发送不成功
        return jsonify(errno=RET.THIRDERR, errmsg="发送短信失败")
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
    print(image_code_id)
    # 2. 判断参数是否有值
    if not image_code_id:
        return abort(403)
    # 3. 生成图片验证码
    name, text, image = captcha.generate_captcha()
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