from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy import and_, or_
from flask_restful import Resource
from .. import api, app
from ..model.friend import Friend
from ..const import ErrNo, result
from .helper import ArgType, JsonArgHelper
from .keys import Key
from application import db


class GetFriendList(Resource):
    """
    This class returns user's friend list.
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
        super(GetFriendList, self).__init__()

    def post(self):
        ret = self.arg_helper.check()
        if ret != ErrNo.OK:
            return result(ret)
        user = self.arg_helper.get_user()
        try:
            return result(ErrNo.OK, list=[friend.to_json() for friend in user.friends])
        except SQLAlchemyError as e:
            app.logger.exception(e)
            return result(ErrNo.DB, msg=str(e))
        return result(ErrNo.OK)


class DelFriend(Resource):
    """
    This class deletes user's friend.
    Parameters:
        token: token get from Login function
        id: friend id
    Errors:
        PARAM: invalid parameter of user input
        DB: database operation failure
        TOKEN: token invalid
    """
    def __init__(self):
        arguments = [(Key.token, True, ArgType.STR, ''),
                     (Key.id, True, ArgType.INT, -1)]
        self.arg_helper = JsonArgHelper(arguments)
        super(DelFriend, self).__init__()

    def post(self):
        ret = self.arg_helper.check()
        if ret != ErrNo.OK:
            return result(ret)
        user = self.arg_helper.get_user()
        friend_id = self.arg_helper.get_param_values()
        try:
            n = db.session.query(Friend).filter(or_(and_(Friend.friend_id == friend_id, Friend.user_id == user.id),
                                                    and_(Friend.friend_id == user.id, Friend.user_id == friend_id))).\
                delete()
            if n == 0:
                return result(ErrNo.NOID)
            db.session.commit()
        except SQLAlchemyError as e:
            app.logger.exception(e)
            msg = str(e)
            return result(ErrNo.DB, msg=msg)
        return result(ErrNo.OK)


class GetFriend(Resource):
    """
    This class get user's friend object according to friend id.
    Parameters:
        token: token get from Login function
        id: friend id
    Errors:
        PARAM: invalid parameter of user input
        DB: database operation failure
        TOKEN: token invalid
    """
    def __init__(self):
        arguments = [(Key.token, True, ArgType.STR, ''),
                     (Key.id, True, ArgType.INT, -1)]
        self.arg_helper = JsonArgHelper(arguments)
        super(GetFriend, self).__init__()

    def post(self):
        ret = self.arg_helper.check()
        if ret != ErrNo.OK:
            return result(ret)
        user = self.arg_helper.get_user()
        friend_id = self.arg_helper.get_param_values()
        try:
            friend = db.session.query(Friend).filter(Friend.user_id==user.id, Friend.friend_id==friend_id).first()
            if friend is None:
                return result(ErrNo.NOID)
            return result(ErrNo.OK, info=friend.to_json())
        except SQLAlchemyError as e:
            app.logger.exception(e)
            msg=str(e)
            return result(ErrNo.DB, msg=msg)


class UpdateFriend(Resource):
    """
    This class handles updates user's friend information, including nick name and
    concessionary fees.
    Parameters:
        token: token get from Login function
        nick: nick name
        appointment: concessionary appointment fee
        electricity: concessionary electricity fee
        service: concessionary service fee
    Errors:
        PARAM: invalid parameter of user input
        DB: database operation failure
        TOKEN: token invalid
        NOID: no corresponding friend id
    """
    def __init__(self):
        arguments = [(Key.token, True, ArgType.STR, ''),
                     (Key.id, True, ArgType.INT, -1),
                     (Key.nick, False, ArgType.STR, ''),
                     (Key.appointment, False, ArgType.DECIMAL, 0.00),
                     (Key.electricity, False, ArgType.DECIMAL, 0.00),
                     (Key.service, False, ArgType.DECIMAL, 0.00)]
        self.arg_helper = JsonArgHelper(arguments)
        super(UpdateFriend, self).__init__()

    def post(self):
        ret = self.arg_helper.check()
        if ret != ErrNo.OK:
            return result(ret)
        user = self.arg_helper.get_user()
        friend_id, nick, appointment, electricity, service = self.arg_helper.get_param_values()
        try:
            friend = db.session.query(Friend).filter(Friend.user_id==user.id, Friend.friend_id==friend_id).first()
            if friend is None:
                return result(ErrNo.NOID)
            if nick != '':
                friend.nick = nick
            if appointment != 0.00:
                friend.appointment = appointment
            if electricity != 0.00:
                friend.electricity = electricity
            if service != 0.00:
                friend.service = service
            db.session.commit()
        except SQLAlchemyError as e:
            app.logger.exception(e)
            msg = str(e)
            return result(ErrNo.DB, msg=msg)
        return result(ErrNo.OK)


api.add_resource(GetFriendList, '/v1/friends/list')
api.add_resource(GetFriend, '/v1/friends/get')
api.add_resource(DelFriend, '/v1/friends/del')
api.add_resource(UpdateFriend, '/v1/friends/update')
