from sqlalchemy.dialects.mysql import MEDIUMBLOB
from .. import db


class FileObj(db.Model):
    """
    This class defines file storage object.

    id : file id
    mime_type : MIME type of the stored file
    obj : binary data

    """
    id = db.Column(db.BigInteger, primary_key=True)
    mime_type = db.Column(db.String(16), nullable=False)
    obj = db.Column(MEDIUMBLOB, nullable=False) # no more than 16M

    def __init__(self, mime_type, obj):
        self.mime_type = mime_type
        self.obj = obj
