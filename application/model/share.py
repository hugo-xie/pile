from .. import db


class Share(db.Model):
    """
    This class defines share record

    id : record id
    user_id : user id
    dt : the date of sharing the information
    time : the times of sharing the information the day.
    """
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.ForeignKey('user.id'))
    dt = db.Column(db.Date)
    time = db.Column(db.SmallInteger)
    db.UniqueConstraint(user_id, dt, time)

    def __init__(self, user_id, dt, time):
        self.user_id = user_id
        self.dt = dt
        self.time = time
