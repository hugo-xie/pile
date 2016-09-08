from .. import db


class Statistic(db.Model):
    """
    This class defines statistics structure.

    id : record id
    user_id : user id
    electricity : total recharged electricity
    cost : total cost
    profit : total profit
    points : total points
    credibility : credibility
    share : total share times
    """
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.ForeignKey('user.id'))
    electricity = db.Column(db.DECIMAL(10, 2))
    cost = db.Column(db.DECIMAL(10, 2))
    profit = db.Column(db.DECIMAL(10, 2))
    points = db.Column(db.Integer)
    credibility = db.Column(db.Integer)
    share = db.Column(db.Integer)

    def __init__(self, user_id, electricity=0, cost=0, profit=0, points=0, credibility=0, share=0):
        self.user_id = user_id
        self.electricity = electricity
        self.cost = cost
        self.profit = profit
        self.points = points
        self.credibility = credibility
        self.share = share

    def to_stat_json(self):
        attrs = ('electricity', 'cost', 'profit', 'points')
        return {attr: self.__getattribute__(attr) for attr in attrs}

    def to_rank_json(self):
        attrs = ('points', 'electricity', 'share', 'credibility')
        return {attr: self.__getattribute__(attr) for attr in attrs}

    def to_json(self):
        attrs = ('id', 'user_id', 'electricity', 'cost', 'profit', 'points', 'credibility', 'share')
        return {attr: self.__getattribute__(attr) for attr in attrs}