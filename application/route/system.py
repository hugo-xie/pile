from datetime import datetime
from .. import api, app
from ..model.message import Message
from ..model.report import Report
from ..model.share import Share
from ..const import ErrNo, result, SettingKey
from .helper import ArgType, JsonArgHelper, store_file
from .keys import Key
from application import db
from sqlalchemy.exc import SQLAlchemyError
from flask_restful import Resource
from .helper import get_setting

class Version(Resource):
    """
    This class returns the program version.
    Errors:
        DB: database operation failure
    """
    def __init__(self):
        super(Version, self).__init__()

    def get_ver(self):
        ver = get_setting(SettingKey.VERSION)
        if ver is None:
            return result(ErrNo.DB)
        return result(ErrNo.OK, version=ver)

    def get(self):
        return self.get_ver()

    def post(self):
        return self.get_ver()


class Messages(Resource):
    """
    This class returns messages.
    Parameters:
        index: the first index user wants to search
        count: the count of messages user wants to search
    Errors:
        DB: database operation failure
    """
    def __init__(self):
        arguments = [(Key.index, False, ArgType.INT, 0),
                     (Key.count, False, ArgType.INT, 50)]
        self.arg_helper = JsonArgHelper(arguments)
        super(Messages, self).__init__()

    def post(self):
        ret = self.arg_helper.check()
        if ret != ErrNo.OK:
            return result(ret)
        index, count = self.arg_helper.get_param_values()
        try:
            messages = db.session.query(Message).filter(Message.id >= index).order_by(Message.id).limit(count).all()
            count = len(messages)
            if count > 0:
                last_index = messages[-1].id + 1
            else:
                last_index = -1
            return result(ErrNo.OK, count=count, index=last_index, messages=[msg.to_json() for msg in messages])
        except SQLAlchemyError as e:
            app.logger.exception(e)
            msg=str(e)
            return result(ErrNo.DB, msg=msg)


class SubmitReport(Resource):
    """
    This class is used for user to report issues. It will save user's comment and photo
    as evidence.

    Parameters:
        token: token get from Login function
        comment: user's comment
        evident: BASE 64 encoded photo

    Errors:
        PARAM: invalid parameter of user input
        DB: database operation failure
        TOKEN: token invalid
    """
    def __init__(self):
        arguments = [
            (Key.token, True, ArgType.STR, ''),
            (Key.comment, True, ArgType.STR, ''),
            (Key.evidence, True, ArgType.BASE64, b''),
        ]
        self.arg_helper = JsonArgHelper(arguments)
        super(SubmitReport, self).__init__()

    def post(self):
        ret = self.arg_helper.check()
        if ret != ErrNo.OK:
            return result(ret)
        user = self.arg_helper.get_user()

        # forbid abusing reports, avoid DoS
        if user.reports.filter(
            Report.handled == False
        ).count() > 5:
            return result(ErrNo.DUP)

        comment = self.arg_helper.get_param(Key.comment)
        if not comment.strip():
            return result(ErrNo.INVALID)

        ret, evidence_id = store_file(self.arg_helper.get_param(Key.evidence))
        if ret != ErrNo.OK:
            return result(ret)

        if evidence_id >= 0:
            evidence_url = '/v1/file/get/' + str(evidence_id)
        else:
            evidence_url = None

        try:
            now = datetime.utcnow()
            report = Report(user.id, evidence_url, comment, now)
            db.session.add(report)
            db.session.commit()
        except SQLAlchemyError as e:
            app.logger.exception(e)
            msg=str(e)
            return result(ErrNo.DB, msg=msg)

        return result(ErrNo.OK, comment=comment, evidence_url=evidence_url)

class RecordShare(Resource):
    """
    This class records the count when user shares the APP on social network websites.
    The user can share no more than twice everyday.

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
        super(RecordShare, self).__init__()

    @staticmethod
    def exists(user, share):
        try:
            db.session.add(share)
            user.statistic.share += 1
            db.session.commit()
            return ErrNo.OK
        except SQLAlchemyError as e:
            db.session.rollback()
            code, msg = e.orig.args
            if code == 1062:
                return ErrNo.DUP
            return ErrNo.DB

    def post(self):
        ret = self.arg_helper.check()
        if ret != ErrNo.OK:
            return result(ret)
        user = self.arg_helper.get_user()
        dt = datetime.now().date()
        share = Share(user.id, dt, 1)
        ret = RecordShare.exists(user, share)
        if ret != ErrNo.DUP:
            return result(ret)
        share = Share(user.id, dt, 2)
        ret = RecordShare.exists(user, share)
        if ret == ErrNo.DUP:
            ret = ErrNo.INVALID
        return result(ret)


api.add_resource(Version, '/v1/system/version')
api.add_resource(Messages, '/v1/system/messages')
api.add_resource(SubmitReport, '/v1/system/report')
api.add_resource(RecordShare, '/v1/system/share')

