from .. import db


class Setting(db.Model):
    """
    This class defines key-value pair record.

    key : information key
    value : information value
    """
    key = db.Column(db.String(64), primary_key=True)
    value = db.Column(db.String(128))

    def __init__(self, key, value):
        self.key = key
        self.value = value

