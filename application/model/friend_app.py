from datetime import datetime
from .. import db
from .helper import to_ts


class FriendApp(db.Model):
    """
    This class defines friend application structure.

    id : record id
    initiator_id : initiator user id
    target_id : target user id
    app_dt : application timestamp
    status : application status
    resp_dt : response timestamp
    initiator : initiator user object (maintained by flask)
    target : target user object (maintained by flask)

    """
    id = db.Column(db.Integer, primary_key=True)
    initiator_id = db.Column(db.ForeignKey('user.id'))
    target_id = db.Column(db.ForeignKey('user.id'))
    app_dt = db.Column(db.DateTime)
    status = db.Column(db.SmallInteger)
    resp_dt = db.Column(db.DateTime)
    initiator = db.relationship('User', foreign_keys=[initiator_id])
    target = db.relationship('User', foreign_keys=[target_id])

    def __init__(self, initiator_id, target_id, app_dt = None, status=0):
        self.initiator_id = initiator_id
        self.target_id = target_id
        self.app_dt = app_dt if app_dt else datetime.utcnow()
        self.status = status

    def to_json(self):
        attrs = ('id', 'initiator_id', 'status')
        json = {attr: self.__getattribute__(attr) for attr in attrs}
        json['app_dt'] = to_ts(self.app_dt)
        if self.resp_dt is not None:
            json['resp_dt'] = to_ts(self.resp_dt)
        json['initiator_name'] = self.initiator.nick
        if self.initiator.avatar is not None:
            json['initiator_avatar'] = self.initiator.avatar
        return json
