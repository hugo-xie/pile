from datetime import datetime, timedelta
from hashlib import md5
from sqlalchemy.exc import SQLAlchemyError
from ..model.session import Session
from .. import db, app
from ..const import ErrNo, TOKEN_TIME_OUT_MIN


def get_token(user_id):
    """
    This function generates token, save it and timestamp to database, and return it.
    """
    string = str(datetime.utcnow()) + str(user_id)
    now = datetime.utcnow()
    ts = now - timedelta(minutes=TOKEN_TIME_OUT_MIN)
    try:
        token = md5(string.encode()).hexdigest()
        s = Session(token, user_id)
        db.session.add(s)
        Session.query.filter(Session.ts < ts).delete()
        db.session.commit()
    except SQLAlchemyError as e:
        return ErrNo.DB, str(e)
    return ErrNo.OK, token


def verify_token(token):
    """
    This function verifies token, and return corresponding user object.
    """
    ts = datetime.utcnow() - timedelta(minutes=TOKEN_TIME_OUT_MIN)
    try:
        Session.query.filter(Session.ts < ts).delete()
        t = Session.query.get(token)
        if t is None:
            return ErrNo.TOKEN, None
        t.ts = datetime.utcnow()
        db.session.commit()
    except SQLAlchemyError as e:
        return ErrNo.DB, str(e)
    return ErrNo.OK, t.user_id


def del_token(token):
    """
    This function deletes the token.
    """
    try:
        s = Session.query.get(token)
        if s is not None:
            db.session.delete(s)
            db.session.commit()
    except SQLAlchemyError as e:
        app.logger.exception(e)
        return ErrNo.DB
    return ErrNo.OK
