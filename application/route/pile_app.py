from .. import api, app
from ..model.pile_app import PileApp
from ..const import ErrNo, result
from .helper import ArgType, JsonArgHelper
from .keys import Key
from application import db
from sqlalchemy.exc import SQLAlchemyError
from flask_restful import Resource


class ApplyPile(Resource):
    """
    This class handles "Update Pile Information" function, it will return the result of update.

    Parameters:
        id: pile id
        name: pile name
        service: service fee
        electricity: electricity fee
        appointment: appointment fee
        open: open time (datetime)
        close: close time (datetime)
        auto_ack: automatically acknowledge
        auto_ack_start: automatically acknowledge start time
        auto_ack_end: automatically acknowledge end time

    Errors:
        PARAM: invalid parameter of user input
        DB: database operation failure
        NOID: cannot find pile according to id
        NOAUTH: is not the owner of the pile
    """
    def __init__(self):
        arguments = [(Key.token, True, ArgType.STR, ''),
                     (Key.choice, True, ArgType.INT, -1),
                     (Key.name, True, ArgType.STR, ''),
                     (Key.ident, True, ArgType.STR, 0.0),
                     (Key.mobile, True, ArgType.STR, 0.0),
                     (Key.comment, False, ArgType.STR, 0.0)]
        self.arg_helper = JsonArgHelper(arguments)
        super(ApplyPile, self).__init__()

    def post(self):
        ret = self.arg_helper.check()
        if ret != ErrNo.OK:
            return result(errno=ret)

        choice, name, ident, mobile, comment = self.arg_helper.get_param_values()

        user = self.arg_helper.get_user()
        pile_app = PileApp(user.id, choice, name, ident, mobile, comment)
        try:
            db.session.add(pile_app)
            db.session.commit()
        except SQLAlchemyError as e:
            app.logger.exception(e)
            return result(errno=ErrNo.DB)
        return result(errno=ErrNo.OK)


class PileAppList(Resource):
    """
    This class returns user's applications for building piles.
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
        super(PileAppList, self).__init__()

    def post(self):
        ret = self.arg_helper.check()
        if ret != ErrNo.OK:
            return result(ret)
        user = self.arg_helper.get_user()
        try:
            return result(errno=ErrNo.OK, list=[app.to_json() for app in user.pile_apps])
        except SQLAlchemyError as e:
            app.logger.exception(e)
            return result(errno=ErrNo.DB, msg=str(e))

api.add_resource(ApplyPile, '/v1/requests/apply')
api.add_resource(PileAppList, '/v1/requests/list')

