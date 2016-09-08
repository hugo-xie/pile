# -*- coding: utf-8 -*-
import random
from datetime import datetime
from flask_restful import Resource
from .sms import SMS
from .keys import Key
from .helper import ArgType, JsonArgHelper
from ..const import CODE_TIME_OUT_SEC, ErrNo, result
from .. import api, db, app
from ..model.code import Code
from sqlalchemy.exc import SQLAlchemyError


def send_code(mobile):
    """
    This function sends code to mobile and updates it in database with new timestamp
    Parameters:
        mobile: mobile phone number
    Errors:
        SMS: failure of sending SMS
        DB: database operation failure
    """
    code = str(random.randint(1000, 9999))
    msg = '【快翼充】您的验证码：' + code + ' 有效期5分钟'
    ret = SMS.send(mobile, msg)
    if ret != ErrNo.OK:
        return ret
    code = Code(mobile, code)
    try:
        db.session.merge(code)
        db.session.commit()
    except SQLAlchemyError:
        return ErrNo.DB
    return ErrNo.OK


def verify_code(mobile, code):
    """
    This function verifies mobile number with corresponding verification code.
    Parameters:
        mobile: mobile phone number
        code: verification code
    Errors:
        DB: database operation failure
        TIMEOUT: verification code invalid due to timeout
        CODE: invalidate verification code
    """
    if app.debug:
        return ErrNo.OK
    try:
        record = Code.query.get(mobile)
    except SQLAlchemyError:
        return ErrNo.DB
    if record is None:
        return ErrNo.INVALID
    if (datetime.utcnow() - record.ts).total_seconds() > CODE_TIME_OUT_SEC:
        return ErrNo.TIMEOUT
    if record.code != code:
        return ErrNo.INVALID
    return ErrNo.OK


class SendCode(Resource):
    """
    This class verifies mobile phone number by sending verification code via SMS.
    Parameters:
        mobile: mobile phone number
    Errors:
        SMS: failure of sending SMS
        DB: database operation failure
    """
    def __init__(self):
        arguments = [(Key.mobile, True, ArgType.STR, '')]
        self.arg_helper = JsonArgHelper(arguments)
        super(SendCode, self).__init__()

    def post(self):
        ret = self.arg_helper.check()
        if ret != ErrNo.OK:
            return result(ret)
        mobile = self.arg_helper.get_param_values()
        ret = send_code(mobile)
        return result(ret)

api.add_resource(SendCode,'/v1/user/code')

