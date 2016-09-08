from datetime import datetime, timedelta
from flask_restful import Resource
from .helper import Key, ArgType, JsonArgHelper, db, SQLAlchemyError, send_mns_action, create_book
from ..const import ADJOIN_BOOK_SPACE_SECONDS, BookStatus, ErrNo, result
from .. import api, app
from ..model.pile import Pile
from ..model.book import Book
from ..model.terminal import TerminalChargeStatus
from ..model.point import Point
from ..route.book_state_machine import on_pay, on_accept, on_decline, on_cancel, on_stop_charge, handle_auto_accept

class BookPile(Resource):
    """
    This class handlers "Book Pile" function. It locks pile time slot table, search a proper time slot, if the time slot
    is found, register this time slot, unlock the table, and return the book id.

    Parameters:
        token: token get from Login function
        pile_id: the id of pile user wants to book
        start: the start time user wants to book
        end: the end time user wants to book

    Errors:
        PARAM: invalid parameter of user input
        DB: database operation failure
        TOKEN: token invalid
        NOID: pile not exists
        INVALID: proper time slot not exists

    """
    def __init__(self):
        arguments = [(Key.token, True, ArgType.STR, ''),
                     (Key.pile_id, True, ArgType.INT, 0),
                     (Key.start, True, ArgType.INT, 0),
                     (Key.end, True, ArgType.INT, 0)]
        self.arg_helper = JsonArgHelper(arguments)
        super(BookPile, self).__init__()

    def post(self):
        ret = self.arg_helper.check()
        if ret != ErrNo.OK:
            return result(ret)
        user_id = self.arg_helper.user.id
        pile_id, start, end = self.arg_helper.get_param_values()
        ret, book, pts = create_book(pile_id, user_id, start, end)

        if ret != ErrNo.OK:
            db.session.rollback()
            return result(ret)

        try:
            ret, bookid, bookstatus = on_pay(book)
            if ret == ErrNo.OK and bookstatus == BookStatus.PAID:
                ret, bookid, bookstatus = handle_auto_accept(book)
            db.session.commit()
            return result(ret, id=bookid, status=bookstatus)
        except SQLAlchemyError as e:
            db.session.delete(book)
            db.session.delete(pts)
            return result(ErrNo.DB, msg=str(e))
        return result(ErrNo.INVALID)


class BookHistory(Resource):
    """
    This class draws user's book list, it will return a list of Book object, the count of the list, index for
    next search

    Parameters:
        token
        type    0：未完成的预约 1：全部预约
        index   从该预约ID开始寻找
        count   返回预约的数量，默认50个

    Errors
        PARAM: invalid parameter of user input
        DB: database operation failure
        TOKEN: token invalid
    """
    def __init__(self):
        arguments = [(Key.token, True, ArgType.STR, ''),
                     (Key.type, True, ArgType.INT, 0),
                     (Key.index, False, ArgType.INT, -1),
                     (Key.count, False, ArgType.INT, 50)]
        self.arg_helper = JsonArgHelper(arguments)
        super(BookHistory, self).__init__()

    def _flatten_book_with_pile(self, book):
        ans = book.to_json()
        ans['pile'] = book.pile.to_json()
        return ans

    def post(self):
        ret = self.arg_helper.check()
        if ret != ErrNo.OK:
            return result(ret)
        user_id = self.arg_helper.user.id
        type, index, count = self.arg_helper.get_param_values()
        if index < 0:
            # make an always true condition
            index_filter = (Book.id >= 0)
        else:
            index_filter = (Book.id <= index)
        try:
            if type == 1:
                books = db.session.query(Book).filter(
                    Book.user_id == user_id,
                    index_filter
                ).order_by(Book.id.desc()).limit(count).all()
            else:
                reservation_end_dt = datetime.utcnow() - timedelta(0, ADJOIN_BOOK_SPACE_SECONDS)
                books = db.session.query(Book).filter(
                    Book.user_id == user_id,
                    index_filter,
                    Book.status != BookStatus.DECLINE.value,
                    Book.status != BookStatus.COMPLETE.value,
                    Book.status != BookStatus.CANCEL.value,
                    Book.book_end > reservation_end_dt
                ).order_by(Book.id.desc()).limit(count).all()
            count = len(books)
            if count > 0 and books[-1].id > 0:
                last_index = books[-1].id - 1
            else:
                last_index = 0
            return result(
                ErrNo.OK, count=count,
                books=[self._flatten_book_with_pile(book) for book in books],
                index=last_index
            )
        except SQLAlchemyError as e:
            return result(ErrNo.DB, msg=str(e))


def cal_stat(user, pile_sn):
    stat = db.session.query(TerminalChargeStatus).filter(TerminalChargeStatus.sn == pile_sn,
                                                  TerminalChargeStatus.ts <= datetime.utcnow()).\
            order_by(TerminalChargeStatus.ts.desc())\
            .first()
    if stat is None:
        return
    amount = int(round(stat.info_charged,0)) + 5
    add_point(user, amount)
    user.statistic.electricity += stat.info_charged


def add_point(user, amount):
    point = Point(user.id, amount)
    db.session.add(point)
    user.statistic.points += amount


class BookAction(Resource):
    """
    This class start or stop charging.

    Parameters:
        token:
        id: book id
        action: 0 start 1 stop 2 cancel 3 flash

    Errors:
        PARAM: invalid parameter of user input
        DB: database operation failure
        TOKEN: token invalid
        NOID: book not exists
        NOAUTH: book not belongs to current user
        INVALID: cannot start or stop because of book's status
    """
    def __init__(self):
        arguments = [(Key.token, True, ArgType.STR, ''),
                     (Key.id, True, ArgType.INT, 0),
                     (Key.action, True, ArgType.INT, 0)]
        self.arg_helper = JsonArgHelper(arguments)
        super(BookAction, self).__init__()

    def start(self, book):
        dt = datetime.utcnow()
        if book.charge_start is None and \
                book.status == BookStatus.ACCEPT.value and \
                book.in_charge_window(dt):
            last_charge_info = TerminalChargeStatus.query.filter(
                TerminalChargeStatus.sn == book.pile.sn
            ).order_by(
                TerminalChargeStatus.ts.desc()
            ).first()
            if last_charge_info is not None:
                book.charged_value_base = last_charge_info.info_charged
            # always set a delay to start message to make sure it is received after the 'book' message
            if not send_mns_action(book.pile.sn, book.id, 'start', delay=1):
                return result(ErrNo.MNS)
            charging_length = int((book.book_end - dt).total_seconds())
            send_mns_action(book.pile.sn, book.id, 'stop', delay=charging_length)
            book.status = BookStatus.CHARGING.value
            book.charge_start = dt
            db.session.commit()
        else:
            if app.debug:
                book.status = BookStatus.CHARGING.value
                book.charge_start = dt
                db.session.commit()
                return result(ErrNo.OK)
            return result(ErrNo.INVALID)
        return result(ErrNo.OK)

    def stop(self, book):
        dt = datetime.utcnow()
        if book.status != BookStatus.CHARGING.value:
            app.logger.error('expecting status %s but got %s', BookStatus.CHARGING.value, book.status)
            return result(ErrNo.INVALID)

        if not send_mns_action(book.pile.sn, book.id, 'stop', delay=1):
            app.logger.error('MNS error happend')
            return result(ErrNo.MNS)

        book.status = BookStatus.COMPLETE.value
        book.charge_end = dt
        if book.time_slot:
            book.time_slot.end = dt
        on_stop_charge(book)
        cal_stat(self.arg_helper.get_user(), book.pile.sn)
        db.session.commit()
        return result(ErrNo.OK)

    def cancel(self, book):
        if book.status not in [
            BookStatus.NPAID.value,
            BookStatus.PAID.value,
            BookStatus.ACCEPT.value,
            BookStatus.DECLINE.value,
        ]:
            return result(ErrNo.INVALID)

        app.logger.debug('cancelled book id %d', book.id)
        if not send_mns_action(book.pile.sn, book.id, 'unbook', delay=1):
            return result(ErrNo.MNS)
        book.status = BookStatus.CANCEL.value
        if book.time_slot:
            db.session.delete(book.time_slot)
        on_cancel(book)
        # if the book is canceled in 30 min before due time, 5 points will be subtracted,
        if (book.book_start - datetime.utcnow()).total_seconds() <= 30 * 60:
            add_point(self.arg_helper.get_user(), -5)
        db.session.commit()
        return result(ErrNo.OK, fee=book.appointment)

    def flash(self, book):
        if book.status not in [
            BookStatus.ACCEPT.value,
            BookStatus.CHARGING.value,
        ]:
            return result(ErrNo.INVALID)
        if not send_mns_action(book.pile.sn, book.id, 'flash'):
            return result(ErrNo.MNS)
        return result(ErrNo.OK)

    def post(self):
        ret = self.arg_helper.check()
        if ret != ErrNo.OK:
            return result(ret)
        id, action = self.arg_helper.get_param_values()
        user_id = self.arg_helper.user.id
        try:
            book = db.session.query(Book).get(id)
            if book is None:
                return result(ErrNo.NOID)
            if book.user_id != user_id:
                return result(ErrNo.NOAUTH)
            action_map = {
                0: self.start,
                1: self.stop,
                2: self.cancel,
                3: self.flash,
            }
            func = action_map.get(action)
            if func:
                ret = func(book)
            else:
                ret = result(ErrNo.INVALID)
            if ret == ErrNo.OK:
                db.session.commit()
        except SQLAlchemyError as e:
            ret = result(ErrNo.DB, msg=str(e))
        except Exception as e:
            db.session.rollback()
            ret = result(ErrNo.INVALID, msg=str(e))
        return ret


class BookInfo(Resource):
    """
    This class searches and returns book information according to book id

    Parameters:
        token:
        id: book id

    Errors:
        PARAM: invalid parameter of user input
        DB: database operation failure
        TOKEN: token invalid
        NOID: book not exists
        NOAUTH: book not belongs to current user
    """
    def __init__(self):
        arguments = [(Key.token, True, ArgType.STR, ''),
                     (Key.id, True, ArgType.INT, 0)]
        self.arg_helper = JsonArgHelper(arguments)
        super(BookInfo, self).__init__()

    def post(self):
        ret = self.arg_helper.check()
        if ret != ErrNo.OK:
            return result(ret)
        id = self.arg_helper.get_param_values()
        user_id = self.arg_helper.user.id
        try:
            book = db.session.query(Book).get(id)
            if book is None:
                return result(ErrNo.NOID)
            if book.user_id != user_id:
                return result(ErrNo.NOAUTH)
            return result(ErrNo.OK, book=book.to_json(with_stat=True))
        except SQLAlchemyError as e:
            app.logger.exception(e)
            return result(ErrNo.DB, msg=str(e))


class PileBooks(Resource):
    """
    This class searches all books of one specific pile.It will return a list of Book object, the count of the list,
    index for next search

    Parameters:
        token:
        id: pile id
        index: pile id that start to search
        count: the length of book list user want to search

    Errors:
        PARAM: invalid parameter of user input
        DB: database operation failure
        TOKEN: token invalid
        NOID: pile not exists
        NOAUTH: pile not belongs to current user
    """
    def __init__(self):
        arguments = [(Key.token, True, ArgType.STR, ''),
                     (Key.id, True, ArgType.INT, 0),
                     (Key.index, False, ArgType.INT, -1),
                     (Key.count, False, ArgType.INT, 50)]
        self.arg_helper = JsonArgHelper(arguments)
        super(PileBooks, self).__init__()

    def post(self):
        ret = self.arg_helper.check()
        if ret != ErrNo.OK:
            return result(ret)
        pile_id, index, count = self.arg_helper.get_param_values()
        if index < 0:
            # make an always true condition
            index_filter = (Book.id >= 0)
        else:
            index_filter = (Book.id <= index)
        try:
            pile = db.session.query(Pile).get(pile_id)
            if pile is None:
                return result(ErrNo.NOID)
            books = db.session.query(Book).filter(Book.pile_id == pile_id, index_filter).order_by(Book.id.desc()).\
                limit(count).all()
            count = len(books)
            if count > 0 and books[-1].id > 0:
                last_index = books[-1].id - 1
            else:
                last_index = 0
            return result(ErrNo.OK, count=count, books=[book.to_json() for book in books], index=last_index)
        except SQLAlchemyError as e:
            app.logger.error('db error during pile book query')
            app.logger.exception(e)
            return result(ErrNo.DB)
        except Exception as e:
            app.logger.error('runtime error during pile book query')
            app.logger.exception(e)
            return result(ErrNo.INVALID)


class ProcessBook(Resource):
    """
    This class is used for pile owner to process book application. Pile owner can accept it or reject it.

    Parameters:
        token: token get from Login function
        id: the id of book application
        accept: whether pile owner accept the application, 0: decline, 1: accept

    Errors:
        PARAM: invalid parameter of user input
        DB: database operation failure
        TOKEN: token invalid
        NOID: book id not exists
        NOAUTH: current user is not pile owner
        INVALID: book status incorrect or time failure

    """
    def __init__(self):
        arguments = [(Key.token, True, ArgType.STR, ''),
                     (Key.id, True, ArgType.INT, 0),
                     (Key.accept, True, ArgType.INT, 0)]
        self.arg_helper = JsonArgHelper(arguments)
        super(ProcessBook, self).__init__()

    def post(self):
        ret = self.arg_helper.check()
        if ret != ErrNo.OK:
            return result(ret)
        user = self.arg_helper.get_user()
        id, accept = self.arg_helper.get_param_values()
        try:
            book = db.session.query(Book).get(id)
            if book is None:
                app.logger.error('no such book %d', id)
                return result(ErrNo.NOID)
            if book.pile.owner_id != user.id:
                app.logger.error('not your pile, owenr is %d, user is %d', book.pile.owner_id, user.id)
                return result(ErrNo.NOAUTH)
            if book.status != BookStatus.PAID.value or (accept and not book.still_on_time()):
                app.logger.error('status or time failure, %s %s', book.status, book.still_on_time())
                return result(ErrNo.INVALID)
            if accept == 0:
                ret = on_decline(book)
            else:
                ret = on_accept(book)
            if ret == ErrNo.OK:
                db.session.commit()
            else:
                db.session.rollback()
            return result(ret)
        except SQLAlchemyError as e:
            app.logger.exception(e)
            msg = str(e)
            return result(ErrNo.DB, msg=msg)

class ChargeRequest(Resource):
    """
    This class searches all pending books to piles owned by current user

    Parameters:
        token: token get from Login function
        index: pile id that start to search
        count: the length of book list user want to search

    Errors:
        PARAM: invalid parameter of user input
        DB: database operation failure
        TOKEN: token invalid
    """
    def __init__(self):
        arguments = [(Key.token, True, ArgType.STR, ''),
                     (Key.index, False, ArgType.INT, -1),
                     (Key.count, False, ArgType.INT, 50)]
        self.arg_helper = JsonArgHelper(arguments)
        super(ChargeRequest, self).__init__()

    def post(self):
        ret = self.arg_helper.check()
        if ret != ErrNo.OK:
            return result(ret)
        user = self.arg_helper.get_user()
        now = datetime.utcnow()
        index, count = self.arg_helper.get_param_values()
        if index < 0:
            # make an always true condition
            index_filter = (Book.id >= 0)
        else:
            index_filter = (Book.id <= index)
        try:
            owned_piles = Pile.query.with_entities(
                Pile.id
            ).filter(
                Pile.owner_id == user.id
            )
            books = db.session.query(Book).filter(
                Book.pile_id.in_(owned_piles),
                Book.status == BookStatus.PAID.value,
                Book.book_end > now,
                index_filter
            ).order_by(
                Book.id.desc()
            ).limit(count).all()
            count = len(books)
            if count > 0 and books[-1].id > 0:
                last_index = books[-1].id - 1
            else:
                last_index = 0
            return result(ErrNo.OK, count=count, books=[book.to_json() for book in books], index=last_index)
        except SQLAlchemyError as e:
            app.logger.error('db error during pile book query')
            app.logger.exception(e)
            return result(ErrNo.DB)
        except Exception as e:
            app.logger.error('runtime error during pile book query')
            app.logger.exception(e)
            return result(ErrNo.INVALID)

api.add_resource(BookPile, '/v1/books/new')
api.add_resource(BookHistory, '/v1/books/all')
api.add_resource(BookAction, '/v1/books/action')
api.add_resource(BookInfo, '/v1/books/info')
api.add_resource(PileBooks, '/v1/books/pile')
api.add_resource(ProcessBook, '/v1/books/process')
api.add_resource(ChargeRequest, '/v1/books/requests')
