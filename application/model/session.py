from datetime import datetime
from .. import db


class Session(db.Model):
    """
    This class defines session structure.

    token : randomized token
    ts : timestamp
    user_id : user id
    """
    token = db.Column(db.String(32), primary_key=True)
    ts = db.Column(db.DateTime, nullable=False)
    user_id = db.Column(db.BigInteger, nullable=False)

    def __init__(self, token, user_id):
        self.token = token
        self.ts = datetime.utcnow()
        self.user_id = user_id

    def __str__(self):
        return 'token %s, ts %s, id %u' % (self.token, self.ts, self.user_id)