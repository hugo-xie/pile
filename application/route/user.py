import string, re
from random import sample
from .. import api, db, app
from ..model.user import User
from ..const import ErrNo, result
from .sms import SMS
from .keys import Key
from .helper import ArgType, JsonArgHelper, store_file, delete_file
from .token import get_token, del_token
from .code import verify_code
from flask_restful import Resource
from sqlalchemy.exc import SQLAlchemyError


class Register(Resource):
    """
    This class handlers user registration.

    Parameters:
    name (*)	用户名
    nick    昵称
    password (*)	密码
    mobile(*)	手机号
    code(*) 验证码
    plate(*)	车牌号
    shell(*)	车架号
    license(*)	行驶证照片
    email(*)	邮箱
    avatar 头像图片

    The error it might return includes:
    PARAM: invalid parameter of user input
    DB: database operation failure
    BIG: photo file too big
    DUP: name or mobile is used
    TIMEOUT: validation code time out
    INCODE: invalid validation code
    """
    def __init__(self):
        arguments = [(Key.name, True, ArgType.STR, ''),
                     (Key.email, True, ArgType.STR, ''),
                     (Key.password, True, ArgType.STR, ''),
                     (Key.mobile, True, ArgType.STR, ''),
                     (Key.code, True, ArgType.STR, ''),
                     (Key.plate, True, ArgType.STR, ''),
                     (Key.shell, True, ArgType.STR, ''),
                     (Key.nick, False, ArgType.STR, ''),
                     (Key.license, True, ArgType.BASE64, b''),
                     (Key.avatar, False, ArgType.BASE64, b'')]
        self.arg_helper = JsonArgHelper(arguments)
        super(Register, self).__init__()

    def post(self):
        ret = self.arg_helper.check()
        if ret != ErrNo.OK:
            return result(ret)
        mobile = self.arg_helper.get_param(Key.mobile)
        code = self.arg_helper.get_param(Key.code)
        ret = verify_code(mobile, code)
        if ret != ErrNo.OK:
            return result(ret)

        ret, avatar_id = store_file(self.arg_helper.get_param(Key.avatar))
        if ret == ErrNo.BIG:
            return result(ret)

        ret, license_id = store_file(self.arg_helper.get_param(Key.license))
        if ret != ErrNo.OK:
            return result(ret)

        args = self.arg_helper.get_param_map()
        del args[Key.code.name]

        if avatar_id >= 0:
            avatar_url = '/v1/file/get/' + str(avatar_id)
        else:
            avatar_url = None
        if license_id >= 0:
            license_url = '/v1/file/get/' + str(license_id)
        else:
            license_url = None
        args[Key.avatar.name] = avatar_url
        args[Key.license.name] = license_url

        user = User(**args)
        try:
            db.session.add(user)
            db.session.commit()
            try:
                user.prepare_user()
                db.session.commit()
            except SQLAlchemyError as e:
                db.session.rollback()
                db.session.delete(user)
                if avatar_id >= 0:
                    delete_file(avatar_id)
                if license_id >= 0:
                    delete_file(license_id)
        except SQLAlchemyError as e:
            if avatar_id >= 0:
                delete_file(avatar_id)
            if license_id >= 0:
                delete_file(license_id)
            code, msg = e.orig.args
            if code == 1062:
                return result(ErrNo.DUP, msg=msg)
            else:
                return result(ErrNo.DB, msg=str(e))
        return result(ErrNo.OK)


def verify_user(user, password):
    """
    Check user login information
    :param user: User object
    :param password:  Password
    :return: (result, user object when login successfully)
        result includes
        NOID: user does not exist
        INACT: user inactive
        PASSWD: incorrect password
    """
    if user is None:
        return ErrNo.NOID, None
    if not user.active:
        return ErrNo.INACT, None
    if not user.verify(password):
        return ErrNo.PASSWD, user
    return ErrNo.OK, user


def login_name(name, password):
    """
    Login with user name and password
    :param name: User name
    :param password: Password
    :return: (result, user object when login successfully)
        error includes
        DB: database operation failure
        NOID: user does not exist
        INACT: user inactive
        PASSWD: incorrect password
    """
    try:
        user = User.query.filter(User.name == name).first()
    except SQLAlchemyError as e:
        app.logger.exception(e)
        return ErrNo.DB,str(e)
    return verify_user(user, password)


def login_mobile(mobile, password):
    """
    Login with mobile and password
    :param mobile: Mobile phone
    :param password: Password
    :return: (result, user object when login successfully)
        error includes
        DB: database operation failure
        NOID: user does not exist
        INACT: user inactive
        PASSWD: incorrect password
    """
    try:
        user = User.query.filter(User.mobile == mobile).first()
    except SQLAlchemyError:
        return ErrNo.DB, None
    return verify_user(user, password)


class Login(Resource):
    """This class handles user login, it returns token when login is successful. Token is required in every user related
    function call.

    Parameters:
        name (*)
        password (*)

    Errors:
        PARAM: invalid parameter of user input
        DB: database operation failure
        NOID: user does not exist
        INACT: user inactive
        PASSWD: incorrect password
    """

    def __init__(self):
        arguments = [(Key.name, True, ArgType.STR, ''),
                     (Key.password, True, ArgType.STR, '')]
        self.arg_helper = JsonArgHelper(arguments)
        super(Login, self).__init__()

    def post(self):
        ret = self.arg_helper.check()
        if ret != ErrNo.OK:
            return result(ret)
        name, password = self.arg_helper.get_param_values()
        ret, user = login_name(name, password)
        if ret == ErrNo.NOID:
            ret, user = login_mobile(name, password)
        if ret == ErrNo.OK:
            ret, token = get_token(user.id)
        if ret != ErrNo.OK:
            return result(ret)
        return result(ret, token=token)


class GetUserInfo(Resource):
    """
    This class handlers "Get User Information" function, it will return user object when successfully.

    Parameters:
        token

    Errors:
        PARAM: invalid parameter of user input
        DB: database operation failure
        NOID: user not exists
    """
    def __init__(self):
        arguments = [(Key.token, True, ArgType.STR, '')]
        self.arg_helper = JsonArgHelper(arguments)
        super(GetUserInfo, self).__init__()

    def post(self):
        ret = self.arg_helper.check()
        if ret != ErrNo.OK:
            return result(ret)
        user = self.arg_helper.get_user()
        return result(ret, user=user.to_json())


class UpdateUserInfo(Resource):
    """
    This class handles "Update User Information" function.

    Parameters:
        token
        nick
        email
        avatar

    Errors:
        PARAM: invalid parameter of user input
        DB: database operation failure
        NOID: user not exists
        BIG: photo file too big
    """
    def __init__(self):
        arguments = [(Key.token, True, ArgType.STR, ''),
                     (Key.nick, False, ArgType.STR, ''),
                     (Key.email, False, ArgType.STR, ''),
                     (Key.avatar, False, ArgType.BASE64, b'')]
        self.arg_helper = JsonArgHelper(arguments)
        super(UpdateUserInfo, self).__init__()

    def post(self):
        ret = self.arg_helper.check()
        if ret != ErrNo.OK:
            return result(ret)
        user = self.arg_helper.get_user()
        nick = self.arg_helper.get_param(Key.nick)
        email = self.arg_helper.get_param(Key.email)
        avatar = user.avatar
        prefix = '/v1/file/get/'
        if avatar is not None and avatar.startswith(prefix):
            old_avatar_id = int(user.avatar[len(prefix):])
        else:
            old_avatar_id = -1
        ret, avatar_id = store_file(self.arg_helper.get_param(Key.avatar))
        if ret == ErrNo.BIG or ret == ErrNo.DB:
            return result(ret)
        if nick != '':
            user.nick = nick
        if email != '':
            user.email = email
        if avatar_id >= 0:
            user.avatar = prefix + str(avatar_id)
        try:
            db.session.commit()
        except SQLAlchemyError as e:
            delete_file(avatar_id)
            return result(ErrNo.DB, msg=str(e))
        if old_avatar_id >= 0 and avatar_id >= 0:
            delete_file(old_avatar_id)
        return result(ErrNo.OK)


class Logout(Resource):
    """
    This class handles "Log Out" function

    Parameters:
        token

    Errors:
        PARAM: invalid parameter of user input
        DB: database operation failure
        NOID: user not exists
    """
    def __init__(self):
        arguments = [(Key.token, True, ArgType.STR, '')]
        self.arg_helper = JsonArgHelper(arguments)
        super(Logout, self).__init__()

    def post(self):
        ret = self.arg_helper.check()
        if ret != ErrNo.OK:
            return result(ret)
        token = self.arg_helper.get_token()
        ret = del_token(token)
        return result(ret)


def random_password():
    """
    This function generates random password which consists of 2 letters, 2
    digits and 2 punctuations.
    :return: the randomized password.
    """
    # remove '0lI01' in password in case of confusion
    letters = re.sub('[OlI]', '', string.ascii_letters)
    digits = re.sub('[01]', '', string.digits)
    return ''.join(sample(sample(letters, 2) + sample(digits, 2) + sample(string.punctuation, 2), 6))


class ResetPassword(Resource):
    """
    This class resets user's password by sending randomized password via SMS.
    Parameters:
        mobile: user's mobile phone number
    Errors:
        PARAM: invalid parameter of user input
        DB: database operation failure
        INVALID: mobile phone number not registered.
    """
    def __init__(self):
        arguments = [(Key.mobile, True, ArgType.STR, '')]
        self.arg_helper = JsonArgHelper(arguments)
        super(ResetPassword, self).__init__()

    def post(self):
        ret = self.arg_helper.check()
        if ret != ErrNo.OK:
            return result(ret)
        mobile = self.arg_helper.get_param_values()
        user = db.session.query(User).filter(User.mobile == mobile).first()
        if user is None:
            return result(ErrNo.INVALID)
        new_pass = random_password()
        msg = '【快翼充】您的新密码是：' + new_pass
        ret = SMS.send(mobile, msg)
        if ret != ErrNo.OK:
            return result(ret)
        try:
            user.password = User.password_md5(new_pass)
            db.session.commit()
        except SQLAlchemyError as e:
            app.logger.exception(e)
            return result(ErrNo.DB, msg=str(e))
        return result(ErrNo.OK)


class UpdatePassword(Resource):
    """
    This class update user's password.
    Parameters:
        token: token get from Login function
        code: verification code sent to user's mobile phone
        password: new password
    Errors:
        PARAM: invalid parameter of user input
        DB: database operation failure
        TOKEN: token invalid
        TIMEOUT: verification code invalid due to timeout
        CODE: invalidate verification code
    """
    def __init__(self):
        arguments = [(Key.token, True, ArgType.STR, ''),
                     (Key.code, True, ArgType.STR, ''),
                     (Key.password, True, ArgType.STR, '')]
        self.arg_helper = JsonArgHelper(arguments)
        super(UpdatePassword, self).__init__()

    def post(self):
        ret = self.arg_helper.check()
        if ret != ErrNo.OK:
            return result(ret)
        user = self.arg_helper.get_user()
        code, password = self.arg_helper.get_param_values()
        if not verify_code(user.mobile, code):
            return result(ErrNo.INVALID)
        user.password = User.password_md5(password)
        try:
            db.session.commit()
            return result(ErrNo.OK)
        except SQLAlchemyError as e:
            app.logger.exception(e)
            msg = str(e)
            return result(ErrNo.DB, msg=msg)


class GetStatistics(Resource):
    """
    This class returns user's statistics information.
    Parameters:
        token: token get from Login function
    Errors:
        PARAM: invalid parameter of user input
        DB: database operation failure
        TOKEN: token invalid
    """
    def __init__(self):
        arguments = [(Key.token, True, ArgType.STR, '')]
        self.arg_helper = JsonArgHelper(arguments)
        super(GetStatistics, self).__init__()

    def post(self):
        ret = self.arg_helper.check()
        if ret != ErrNo.OK:
            return result(ret)
        user = self.arg_helper.get_user()
        try:
            return result(ErrNo.OK, sum=user.statistic.to_stat_json())
        except SQLAlchemyError as e:
            return result(ErrNo.DB, msg=str(e))


class GetRank(Resource):
    """
    This class returns user's rank
    Parameters:
        token: token get from Login function
    Errors:
        PARAM: invalid parameter of user input
        DB: database operation failure
        TOKEN: token invalid
    """
    def __init__(self):
        arguments = [(Key.token, True, ArgType.STR, '')]
        self.arg_helper = JsonArgHelper(arguments)
        super(GetRank, self).__init__()

    def post(self):
        ret = self.arg_helper.check()
        if ret != ErrNo.OK:
            return result(ret)
        user = self.arg_helper.get_user()
        try:
            return result(ErrNo.OK, rank=user.statistic.to_rank_json())
        except SQLAlchemyError as e:
            return result(ErrNo.DB, msg=str(e))


api.add_resource(Register, '/v1/user/register')
api.add_resource(Login, '/v1/user/login')
api.add_resource(GetUserInfo, '/v1/user/info')
api.add_resource(UpdateUserInfo, '/v1/user/update')
api.add_resource(Logout, '/v1/user/logout')
api.add_resource(ResetPassword, '/v1/user/reset_password')
api.add_resource(UpdatePassword, '/v1/user/update_password')
api.add_resource(GetStatistics, '/v1/user/statistics')
api.add_resource(GetRank, '/v1/user/rank')
