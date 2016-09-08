from datetime import datetime
from .. import db

class Point(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    amount = db.Column(db.Integer)
    dt = db.Column(db.DateTime)

    def __init__(self, user_id, amount, dt=None):
        self.user_id = user_id
        self.amount = amount
        self.dt = dt if dt else datetime.utcnow()
