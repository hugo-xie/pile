from datetime import  datetime
from .helper import to_ts
from .. import db


class Report(db.Model):
    """
    This class defines report structure.

    id : record id
    user_id : user id
    comment : comment
    evidence : evidence
    dt : timestamp
    handled : whether the report is handled
    """
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.ForeignKey('user.id'))
    comment = db.Column(db.Text())
    evidence = db.Column(db.String(80))
    dt = db.Column(db.DateTime)
    handled = db.Column(db.Boolean)

    def __init__(self, user_id, evidence, comment, dt=None, handled=False):
        self.user_id = user_id
        self.comment = comment
        self.evidence = evidence
        self.dt = dt if dt else datetime.utcnow()
        self.handled = handled

    def to_json(self):
        attrs = ('id', 'user_id', 'comment', 'evidence', 'handled')
        ans = {attr: getattr(self, attr, None) for attr in attrs}
        ans['dt'] = to_ts(self.dt)
        return ans
