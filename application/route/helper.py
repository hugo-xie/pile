from .keys import Key
from ..const import ErrNo, ADJOIN_BOOK_SPACE_SECONDS, UPLOAD_SIZE, BookStatus
from ..model.user import User
from ..model.friend import Friend
from ..model.setting import Setting
from ..model.pile import Pile
from ..model.book import Book
from ..model.pile_time_slot import PileTimeSlot
from ..model.fileobj import FileObj
from ..mns.helper import Account, Message, get_or_create_queue, send_queue_msg
from .. import app, db
from .token import verify_token
from sqlalchemy import or_, and_
from sqlalchemy.exc import SQLAlchemyError
from flask_restful import reqparse
from decimal import Decimal
from json import dumps
from enum import Enum
from simplejson import loads, JSONDecodeError
from flask import request
from base64 import decodebytes
from datetime import datetime
import binascii


class ArgType(Enum):
    """
    This enum defines data types of parameter input by user
    """
    INT = 0
    HEX = 1
    STR = 2
    FLOAT = 3
    DECIMAL = 4
    BASE64 = 5


class ArgHelper:
    """
    This class helps to format user's input and covert to corresponding data, and check
    whether the token is correct if the token is included in parameters.
    """
    def __init__(self, args):
        self.result = []
        self.params = dict()
        self.user = None
        self.token = None
        self.args = args

    def get_param_values(self):
        cnt = len(self.result)
        if cnt == 0:
            return None
        if cnt == 1:
            return self.result[0]
        return tuple(self.result)

    def get_param_map(self):
        return self.params

    def get_param(self, key):
        if key.name in self.params:
            return self.params[key.name]
        return None

    def get_user(self):
        return self.user

    def get_token(self):
        return self.token

    def remove_param(self, key):
        del self.params[key.name]

    def parse_params(self):
        return ErrNo.OK

    def check_type(self, param, tp):
        ret = ErrNo.OK
        value = None
        if tp == ArgType.INT:
            try:
                value = int(param)
            except ValueError:
                ret = ErrNo.PARAM
        elif tp == ArgType.HEX:
            try:
                value = int(param, 16)
            except ValueError:
                ret = ErrNo.PARAM
        elif tp == ArgType.FLOAT:
            try:
                value = float(param)
            except ValueError:
                ret = ErrNo.PARAM
        elif tp == ArgType.DECIMAL:
            try:
                value = Decimal(param)
            except ValueError:
                ret = ErrNo.PARAM
        elif tp == ArgType.BASE64:
            try:
                value = decodebytes(bytes(param, encoding=request.charset))
            except binascii.Error:
                ret = ErrNo.PARAM
        elif tp == ArgType.STR:
            try:
                value = str(param)
            except ValueError:
                ret = ErrNo.PARAM
        return ret, value

    def check(self):
        ret = self.parse_params()
        if ret != ErrNo.OK:
            return ret
        if self.params is None:
            self.params = {}
        for key, mandatory, ty, default in self.args:
            if key.name not in self.params or \
                    (type(self.params[key.name]) == str and len(self.params[key.name]) == 0):
                if mandatory:
                    app.logger.error("Parameter " + key.name + " lost")
                    return ErrNo.PARAM
                else:
                    ret = ErrNo.OK
                    value = default
            else:
                param = self.params[key.name]
                ret, value = self.check_type(param, ty)
            if ret != ErrNo.OK:
                app.logger.error("Parameter " + key.name + " invalid")
                return ret
            if Key.token.name != key.name:
                self.params[key.name] = value
                self.result.append(self.params[key.name])
            else:
                self.token = self.params[Key.token.name]
                del(self.params[Key.token.name])
        if self.token is not None:
            ret, user_id = verify_token(self.token)
            if ret != ErrNo.OK:
                app.logger.error('invalid token in request')
                return ret
            try:
                self.user = User.query.get(user_id)
            except SQLAlchemyError as ex:
                app.logger.error('error happened in user query')
                app.logger.exception(ex)
                return ErrNo.DB
            if self.user is None:
                app.logger.error('no such user %s', user_id)
                return ErrNo.NOID
        return ErrNo.OK


class JsonArgHelper(ArgHelper):
    """
    This class helps to format user's parameters if they are submit in JSON format.
    """
    def __init__(self, args):
        super(JsonArgHelper, self).__init__(args)

    def parse_params(self):
        if len(request.data) == 0:
            app.logger.error('request data is blank.')
            return ErrNo.PARAM
        app.logger.info('%s %s', request.url, request.data)
        try:
            self.params = loads(str(request.data, encoding=request.charset))
        except JSONDecodeError as e:
            app.logger.error('request data conversion failed.')
            app.logger.exception(e)
            return ErrNo.PARAM
        return ErrNo.OK


class FormArgHelper(ArgHelper):
    """
    This class helps to format user's parameters if they are submit in POST/GET format.
    """
    def __init__(self, args):
        self.reqparse = reqparse.RequestParser()
        for key, mandatory, ty, default in args:
            self.reqparse.add_argument(key.name, type=str, default='')
        super(FormArgHelper, self).__init__(args)

    def parse_params(self):
        self.params = self.reqparse.parse_args()
        return ErrNo.OK


def get_setting(key):
    """
    This function get value according to key from key-value table in database.
    """
    try:
        item = db.session.query(Setting).get(key.name)
        if item is None:
            return None
        return item.value
    except SQLAlchemyError:
        return None


def set_setting(key, value):
    """
    This function saves key-value pair in database.
    """
    try:
        item = Setting(key.name, value)
        db.session.merge(item)
        db.session.commit()
        return True
    except SQLAlchemyError:
        return False

def send_mns_action(pile_sn, bookid, action, delay=0, additional=None):
    if app.debug:
        return True
    try:
        queue = get_or_create_queue(
            Account(
                app.config['MNS_HOST'],
                app.config['MNS_ACCESS_ID'],
                app.config['MNS_ACCESS_KEY']
            ),
            pile_sn
        )
        if delay:
            msg = Message()
            msg.delay_seconds = delay
        else:
            msg = None
        content = dict(
            action = action,
            bookid = bookid
        )
        if additional:
            content.update(additional)
        ret = send_queue_msg(
            queue,
            dumps(content),
            msg
        )
    except Exception as ex:
        ret = False
        app.logger.error('MNS exception happened when handling %s %s %s:', pile_sn, bookid, action)
        app.logger.exception(ex)

    return bool(ret)

def create_book(pile_id, user_id, start, end):
    start_dt = datetime.utcfromtimestamp(start)
    end_dt = datetime.utcfromtimestamp(end)
    reservation_start_dt = datetime.utcfromtimestamp(start-ADJOIN_BOOK_SPACE_SECONDS)
    reservation_end_dt = datetime.utcfromtimestamp(end+ADJOIN_BOOK_SPACE_SECONDS)
    book = None
    pts = None
    ret = ErrNo.OK
    try:
        pile = Pile.query.get(pile_id)
        if pile is None:
            return ErrNo.NOID, book, pts
        if start_dt.time() < pile.open or end_dt.time() > pile.close:
            return ErrNo.INVALID, book, pts
        
        if user_id != pile.owner_id:
            friend = db.session.query(Friend).filter(
                Friend.user_id == pile.owner_id,
                Friend.friend_id == user_id).first()
        else:
            friend = None

        app.logger.debug('going to lock the tables with %s', db.session)
        db.session.execute('LOCK TABLES pile_time_slot WRITE, book WRITE;')
        app.logger.debug('tables locked with %s', db.session)

        # need to avoid 4 types of overlapping:
        #
        # A      +---------------+
        # B          +-------+
        #
        # A      +---------+
        # B  +--------+
        #
        # A  +--------+
        # B       +---------+
        #
        # A         +-------+
        # B     +--------------+
        record = db.session.query(PileTimeSlot).filter(
            PileTimeSlot.pile_id == pile_id,
            PileTimeSlot.book.any(
                or_(
                    Book.status.in_([
                        BookStatus.ACCEPT.value,
                        BookStatus.CHARGING.value,
                    ]),
                    and_(
                        Book.user_id == user_id,
                        Book.status.in_([
                            BookStatus.DECLINE.value,
                            BookStatus.NPAID.value,
                            BookStatus.PAID.value,
                        ])
                    )
                )
            ),
            PileTimeSlot.start <= reservation_end_dt,
            PileTimeSlot.end >= reservation_start_dt
        )
        if record.count() == 0:
            pts = PileTimeSlot(pile_id, start_dt, end_dt)
            db.session.add(pts)
            book = Book(
                user_id, pile_id, start_dt, end_dt,
                pile.electricity, pile.service, pile.appointment,
                None
            )
            book.time_slot = pts

            # Pile is booked by its owner
            if pile.owner_id == user_id:
                book.electricity = 0
                book.service = 0
                book.appointment = 0

            # Update some data if they are friends
            if friend is not None:
                if friend.electricity >= 0:
                    book.electricity = friend.electricity
                if friend.service >= 0:
                    book.service = friend.service
                if friend.appointment >= 0:
                    book.appointment = friend.appointment
            db.session.add(book)
            db.session.flush()
            app.logger.debug('new book id %s', book.id)
        else:
            #app.logger.info('found %s reserved slots', list(record.all()))
            app.logger.info(
                'found %s reserved slots, first 5 ids: %s',
                record.count(), [p.id for p in record.limit(5).all()]
            )
            ret = ErrNo.INVALID

    except SQLAlchemyError as ex:
        app.logger.error('database error %s', str(ex))
        app.logger.exception(ex)
        ret = ErrNo.DB
    except Exception as ex:
        app.logger.error('encounter %s error during booking', str(ex))
        app.logger.exception(ex)
        ret = ErrNo.INVALID
    try:
        app.logger.debug('going to unlock the table with %s', db.session)
        db.session.execute('UNLOCK TABLES;')
        app.logger.debug('table unlocked')
    except Exception as ex:
        app.logger.error('encounter %s error during unlocking with %s', str(ex), db.session)
        app.logger.exception(ex)
        ret = ErrNo.INVALID
    return ret, book, pts

def store_file(content, id=-1):
    """
    Store binary stream into database
    currently MIME type is fixed to 'PNG', it may detect MIME automatically in future.
    :param content: byte array
    :param id: used to replace existed record
    :return: (result, record id)
            result includes OK, PARAM, BIG, DB
            PARAM: byte length is 0
            BIG: byte length exceeds database limit
            DB: database operation failure
    """
    if len(content) > UPLOAD_SIZE:
        return ErrNo.BIG, -1
    if len(content) == 0:
        return ErrNo.PARAM, -1
    mime = 'image/png'
    try:
        if id == -1:
            fobj = FileObj(mime_type=mime, obj=content)
            db.session.add(fobj)
        else:
            fobj = FileObj.query.get(id)
            if fobj is None:
                fobj = FileObj(mime_type=mime, obj=content)
            else:
                fobj.mime_type = mime
                fobj.obj = content
            db.session.merge(fobj)
        db.session.commit()
    except SQLAlchemyError:
        return ErrNo.DB, -1
    return ErrNo.OK, fobj.id


def save_file(key, id = -1):
    """ Legacy function used to insert binary stream to database from form post data, it should be removed later
    :param key:
    :param id:
    :return:
    """
    if key.name not in request.files.keys():
        return ErrNo.PARAM, -1
    file = request.files[key.name]
    if not file:
        return ErrNo.PARAM, -1
    content = file.read()
    if len(content) > UPLOAD_SIZE:
        return ErrNo.BIG, -1

    try:
        if id == -1:
            fobj = FileObj(mime_type=file.mimetype, obj=content)
            db.session.add(fobj)
        else:
            fobj = FileObj.query.get(id)
            if fobj is None:
                fobj = FileObj(mime_type=file.mimetype, obj=content)
                fobj.id = id
            else:
                fobj.mime_type = file.mimetype
                fobj.obj = content
            db.session.merge(fobj)
        db.session.commit()
    except SQLAlchemyError:
        return ErrNo.DB, -1
    return ErrNo.OK, fobj.id


def delete_file(id):
    """
    Delete saved file in database
    :param id: saved file id in database
    :return:
        OK: Successful
        DB: Database operation failure
    """

    try:
        fobj = FileObj.query.get(id)
        if fobj is not None:
            db.session.delete(fobj)
            db.session.commit()
    except SQLAlchemyError:
        return ErrNo.OK
    return ErrNo.DB

