from .. import db


class PileTimeSlot(db.Model):
    """
    This class defines booked time slot structure of an application

    id : record id
    pile_id : pile id
    start : start timestamp
    end : end timestamp
    book : corresponding book information
    """
    id = db.Column(db.Integer, primary_key=True)
    pile_id = db.Column(db.Integer, db.ForeignKey('pile.id'))
    start = db.Column(db.DateTime)
    end = db.Column(db.DateTime)
    book = db.relationship('Book', backref='time_slot', lazy='dynamic')

    def __init__(self, pile_id, start, end):
        self.pile_id = pile_id
        self.start = start
        self.end = end

