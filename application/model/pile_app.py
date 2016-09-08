from datetime import datetime
from .helper import to_ts
from .. import db


class PileApp(db.Model):
    """
    This class defines recharge application structure.

    id : record id
    owner_id : owner id
    dt : application timestamp
    choice : <TODO>
    name : user name
    ident : user id card number
    mobile : mobile phone number
    memo : memo
    """
    id = db.Column(db.Integer, primary_key=True)
    owner_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    dt = db.Column(db.DateTime, nullable=False)
    choice = db.Column(db.SmallInteger, nullable=False)
    name = db.Column(db.String(32), nullable=False)
    ident = db.Column(db.String(64), nullable=False)
    mobile = db.Column(db.String(32), nullable=False)
    memo = db.Column(db.String(128))

    def __init__(self, owner_id, choice, name, ident, mobile, memo, dt=None):
        self.owner_id = owner_id
        self.dt = dt if dt else datetime.utcnow()
        self.choice = choice
        self.name = name
        self.ident = ident
        self.mobile = mobile
        self.memo = memo

    def to_json(self):
        attrs = ('id', 'owner_id', 'choice', 'name', 'ident', 'mobile', 'memo')
        json = {attr: self.__getattribute__(attr) for attr in attrs}
        json['dt'] = to_ts(self.dt)
        return json
