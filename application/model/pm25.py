from .helper import to_ts
from .. import db

class DailyPm25(db.Model):
    date = db.Column(db.Date, primary_key=True)
    peak = db.Column(db.Integer)
    valley = db.Column(db.Integer)
    count = db.Column(db.Integer)
    average10x = db.Column(db.Integer)

    def to_json(self):
        ans = dict()
        for key in ('year', 'month', 'day'):
            ans[key] = getattr(self.date, key)
        for key in ('peak', 'valley'):
            ans[key] = getattr(self, key)
        ans['average'] = '%d.%d' % (self.average10x // 10, self.average10x % 10)
        return ans

class HourlyPm25(db.Model):
    hour = db.Column(db.DateTime(), primary_key=True)
    peak = db.Column(db.Integer)
    valley = db.Column(db.Integer)
    count = db.Column(db.Integer)
    average10x = db.Column(db.Integer)

    def to_json(self):
        ans = dict()
        for key in ('peak', 'valley'):
            ans[key] = getattr(self, key)
        ans['timestamp'] = to_ts(self.hour)
        ans['average'] = '%d.%d' % (self.average10x // 10, self.average10x % 10)
        return ans
