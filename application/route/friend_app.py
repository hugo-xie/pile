from sqlalchemy.exc import SQLAlchemyError
from flask_restful import Resource
from ..model.user import User
from ..model.friend_app import FriendApp
from ..model.friend import Friend
from .. import api, app
from ..const import ErrNo, result
from .helper import ArgType, JsonArgHelper
from .keys import Key
from application import db


class AddFriend(Resource):
    """
    This class sends friend application to other users.
    Parameters:
        token: token get from Login function
        mobile: other user's mobile phone
    Errors:
        PARAM: invalid parameter of user input
        DB: database operation failure
        TOKEN: token invalid
        NOID: mobile phone not registered
        INVALID: cannot add oneself friend
        DUP: friend has been added
    """
    def __init__(self):
        arguments = [(Key.token, True, ArgType.STR, ''),
                     (Key.mobile, True, ArgType.STR, '')]
        self.arg_helper = JsonArgHelper(arguments)
        super(AddFriend, self).__init__()

    def post(self):
        ret = self.arg_helper.check()
        if ret != ErrNo.OK:
            return result(ret)
        mobile = self.arg_helper.get_param_values()
        user = self.arg_helper.get_user()
        try:
            target = db.session.query(User).filter(User.mobile==mobile).first()
            if target is None:
                return result(ErrNo.NOID)
            if target.mobile == user.mobile:
                return result(ErrNo.INVALID)
            if user.friends.filter(
                Friend.friend_id == target.id
            ).count():
                return result(ErrNo.DUP)
            if target.friend_apps.filter(
                FriendApp.initiator_id == user.id,
                FriendApp.status == 0
            ).count():
                return result(ErrNo.DUP)
            fapp = FriendApp(user.id, target.id)
            db.session.add(fapp)
            db.session.commit()
        except SQLAlchemyError as e:
            app.logger.exception(e)
            return result(ErrNo.DB, msg=str(e))
        return result(ErrNo.OK)


class ListFriendApp(Resource):
    """
    This class lists friend applications the user receives.
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
        super(ListFriendApp, self).__init__()

    def post(self):
        ret = self.arg_helper.check()
        if ret != ErrNo.OK:
            return result(ret)
        user = self.arg_helper.get_user()
        try:
            apps = user.friend_apps
            return result(ErrNo.OK, list=[fapp.to_json() for fapp in apps])
        except SQLAlchemyError as e:
            app.logger.exception(e)
            return result(ErrNo.DB, msg=str(e))


class ProcessFriendApp(Resource):
    """
    This class handles user's friend application from other users.
    Parameters:
        token: token get from Login function
        id: friend application id
        accept:
            0: reject
            1: accept
    Errors:
        PARAM: invalid parameter of user input
        DB: database operation failure
        TOKEN: token invalid
        NOID: no corresponding friend application
        INVALID: the application has been handled.
    """
    def __init__(self):
        arguments = [(Key.token, True, ArgType.STR, ''),
                     (Key.id, True, ArgType.INT, -1),
                     (Key.accept, True, ArgType.INT, -1)]
        self.arg_helper = JsonArgHelper(arguments)
        super(ProcessFriendApp, self).__init__()

    def post(self):
        ret = self.arg_helper.check()
        if ret != ErrNo.OK:
            return result(ret)
        req_id, accept = self.arg_helper.get_param_values()
        try:
            req = db.session.query(FriendApp).get(req_id)
            if req is None:
                return result(ErrNo.NOID)
            if req.status != 0:
                return result(ErrNo.INVALID)
            if accept == 0:
                req.status = 2

            else:
                req.status = 1
                friend = Friend(req.initiator_id, req.target_id)
                db.session.add(friend)
                friend = Friend(req.target_id, req.initiator_id)
                db.session.add(friend)
            db.session.commit()
        except SQLAlchemyError as e:
            app.logger.exception(e)
            return result(ErrNo.DB, msg=str(e))
        return result(ErrNo.OK)


api.add_resource(AddFriend, '/v1/friends/add')
api.add_resource(ListFriendApp, '/v1/friends/list_req')
api.add_resource(ProcessFriendApp, '/v1/friends/process_req')

