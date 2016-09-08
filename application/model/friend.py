from .. import db


class Friend(db.Model):
    """
    This class defines friend structure.

    id : record id
    user_id : user id
    friend_id : friend id
    nick : nick name
    appointment : appointment fee
    service : service fee
    electricity : electricity fee

    """
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    friend_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    nick = db.Column(db.String(32))
    appointment = db.Column(db.DECIMAL(10, 2))
    service = db.Column(db.DECIMAL(10, 2))
    electricity = db.Column(db.DECIMAL(10, 2))
    target = db.relationship('User', foreign_keys=[friend_id,], uselist=False)

    def __init__(self, user_id, friend_id, appointment=-1, service=-1, electricity=-1):
        self.user_id = user_id
        self.friend_id = friend_id
        self.appointment = appointment
        self.service = service
        self.electricity = electricity

    def to_json(self):
        attrs = ['friend_id']
        optional = ['appointment', 'service', 'electricity']
        if self.nick is not None:
            attrs.append('nick')
        json = {attr: self.__getattribute__(attr) for attr in attrs + optional}
        for k in optional:
            if json[k] < 0: json[k] = -1
        if self.target.nick is not None:
            json['friend_nick'] = self.target.nick
        if self.target.avatar is not None:
            json['friend_avatar'] = self.target.avatar
        return json

