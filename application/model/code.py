from datetime import datetime
from .. import db


class Code(db.Model):
    """
    This class defines verification code structure.

    mobile : the mobile phone number
    ts : timestamp
    code : verification code

    """

    mobile = db.Column(db.String(16), primary_key=True)
    ts = db.Column(db.DateTime, nullable=False)
    code = db.Column(db.String(8), nullable=False)

    def __init__(self, mobile, code):
        self.mobile = mobile
        self.code = code
        self.ts = datetime.utcnow()

    def __str__(self):
        return 'mobile %s, ts %s, code %s' % (self.mobile, self.ts, self.code)