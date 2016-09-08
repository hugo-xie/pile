from datetime import datetime
from .. import db
from .helper import to_ts


class Message(db.Model):
    """
    This class defines messages structure.

    id : record id
    dt : timestamp
    title : message title
    content : message content
    """
    id = db.Column(db.Integer, primary_key=True)
    dt = db.Column(db.DateTime)
    title = db.Column(db.String(80))
    content = db.Column(db.String(1024))

    def __init__(self, title, content, dt=None):
        self.dt = dt if dt else datetime.utcnow()
        self.title = title
        self.content = content

    def to_json(self):
        attrs = ('id', 'title', 'content')
        json = {attr: self.__getattribute__(attr) for attr in attrs}
        json['time'] = to_ts(self.dt)
        return json
