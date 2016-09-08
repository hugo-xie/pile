from flask_restful import Resource
from .. import app
from .keys import Key
from .helper import ArgType, JsonArgHelper, create_book, send_mns_action
from ..const import ErrNo, result, BookStatus, CARD_CHARGE_DURATION_SECONDS
from .. import api, db
from ..model.terminal import Terminal, TerminalInfo, TerminalChargeStatus, TerminalImage
from ..model.pile import Pile
from ..model.book import Book
from ..model.pm25 import DailyPm25, HourlyPm25
from ..model.helper import to_dt, to_ts, extract_date, extract_hour_dt
from sqlalchemy.exc import SQLAlchemyError
from datetime import datetime


class RegTerm(Resource):
    """
    This class registers piles.

    Parameters:
        mobile: mobile number embedded in the pile
        sn: pile serial number
        action:
            1: register
            0: deregister

    Errors:
        DB: database operation failure
        PARAM: invalid parameter of user input
    """
    ACTION_STATUS_MAP = {
        'register': 1,
        'deregister': 0,
    }

    def __init__(self):
        arguments = [ (Key.mobile, True, ArgType.STR, ""),
                      (Key.sn, True, ArgType.STR, ""),
                      (Key.action, False, ArgType.STR, "register")
                    ]
        self.arg_helper = JsonArgHelper(arguments)
        super(RegTerm, self).__init__()

    def post(self):
        ret = self.arg_helper.check()
        if ret != ErrNo.OK:
            return result(ret)
        mobile, sn, action = self.arg_helper.get_param_values()
        if action not in self.ACTION_STATUS_MAP:
            return result(ErrNo.INVALID)
        status = self.ACTION_STATUS_MAP[action]
        terminal = Terminal(mobile, sn, status)
        try:
            db.session.add(terminal)
            db.session.commit()
        except SQLAlchemyError:
            return result(ErrNo.DB)
        return result(ErrNo.OK)

class NewTermInfo(Resource):
    """
    This class registers piles.

    Parameters:
        mobile: mobile number embedded in the pile
        sn: pile serial number
        stat_gun: gun status
        stat_lock: lock status
        stat_charge: charge status
        stat_run: run status
        stat_net:
        stat_battery: battery status
        stat_work:
        info_temp1:
        info_temp2:
        info_temp2:
        info_pm25: pm2.5 value


    Errors:
        DB: database operation failure
        PARAM: invalid parameter of user input
    """
    def __init__(self):
        args = [ (Key.mobile, True, ArgType.STR, ""),
                 (Key.sn, True, ArgType.STR, ""),
                 (Key.stat_gun, True, ArgType.INT, 0),
                 (Key.stat_lock, True, ArgType.INT, 0),
                 (Key.stat_charge, True, ArgType.INT, 0),
                 (Key.stat_run, True, ArgType.INT, 0),
                 (Key.stat_net, True, ArgType.INT, 0),
                 (Key.stat_battery, True, ArgType.INT, 0),
                 (Key.stat_work, True, ArgType.INT, 0),
                 (Key.info_temp1, True, ArgType.DECIMAL, 0),
                 (Key.info_temp2, True, ArgType.DECIMAL, 0),
                 (Key.info_temp3, True, ArgType.DECIMAL, 0),
                 (Key.info_pm25, True, ArgType.DECIMAL, 0)]
        self.arg_helper = JsonArgHelper(args)
        super(NewTermInfo, self).__init__()

    def update_hourly_pm25(self, info):
        hour_dt = extract_hour_dt(info.ts)
        pm25 = HourlyPm25.query.filter(
            HourlyPm25.hour == hour_dt
        ).with_for_update().first()
        if not pm25:
            pm25 = HourlyPm25()
            pm25.hour = hour_dt
            pm25.count = 1
            pm25.average10x = info.info_pm25 * 10
            pm25.peak = pm25.valley = info.info_pm25
            db.session.add(pm25)
        else:
            if pm25.peak < info.info_pm25:
                pm25.peak = info.info_pm25
            if pm25.valley > info.info_pm25:
                pm25.valley = info.info_pm25
            pm25.average10x = \
                (
                    HourlyPm25.average10x * HourlyPm25.count \
                            + info.info_pm25 * 10
                ) / (
                    HourlyPm25.count + 1
                )
            pm25.count = HourlyPm25.count + 1

    def update_daily_pm25(self, info):
        date = extract_date(info.ts)
        pm25 = DailyPm25.query.filter(
            DailyPm25.date == date
        ).with_for_update().first()
        if not pm25:
            pm25 = DailyPm25()
            pm25.date = date
            pm25.count = 1
            pm25.average10x = info.info_pm25 * 10
            pm25.peak = pm25.valley = info.info_pm25
            db.session.add(pm25)
        else:
            if pm25.peak < info.info_pm25:
                pm25.peak = info.info_pm25
            if pm25.valley > info.info_pm25:
                pm25.valley = info.info_pm25
            pm25.average10x = \
                (
                    DailyPm25.average10x * DailyPm25.count \
                            + info.info_pm25 * 10
                ) / (
                    DailyPm25.count + 1
                )
            pm25.count = DailyPm25.count + 1

    def post(self):
        ret = self.arg_helper.check()
        if not ret:
            return result(ret)
        info = TerminalInfo(**self.arg_helper.get_param_map())
        try:
            db.session.add(info)
            db.session.flush()
            self.update_daily_pm25(info)
            self.update_hourly_pm25(info)
            db.session.commit()
        except SQLAlchemyError:
            return result(ErrNo.DB)
        return result(ErrNo.OK)


class NewTermChargeStat(Resource):
    """
    This class adds terminal's charge status.

    Parameters:
        mobile: mobile number embedded in the pile
        sn: pile serial number
        info_duration: duration value
        info_charged: charged value
        info_current: current value
        info_volt: voltage value

    Errors:
        DB: database operation failure
        PARAM: invalid parameter of user input
    """
    def __init__(self):
        args = [ (Key.mobile, True, ArgType.STR, ""),
                 (Key.sn, True, ArgType.STR, ""),
                 (Key.info_duration, True, ArgType.DECIMAL, 0),
                 (Key.info_charged, True, ArgType.DECIMAL, 0),
                 (Key.info_current, True, ArgType.DECIMAL, 0),
                 (Key.info_volt, True, ArgType.DECIMAL, 0),]
        self.arg_helper = JsonArgHelper(args)
        super(NewTermChargeStat, self).__init__()

    def post(self):
        ret = self.arg_helper.check()
        if not ret:
            return result(ret)
        stat = TerminalChargeStatus(**self.arg_helper.get_param_map())
        try:
            db.session.add(stat)
            db.session.commit()
        except SQLAlchemyError:
            return result(ErrNo.DB)
        return result(ErrNo.OK)

class Permission(Resource):
    """


    Parameters:


    Errors:
        DB: database operation failure
        PARAM: invalid parameter of user input
    """
    permission_matrix = {
        'book': [BookStatus.ACCEPT.value, BookStatus.CHARGING.value],
        'start': [BookStatus.ACCEPT.value, BookStatus.CHARGING.value],
        'flash': [BookStatus.ACCEPT.value, BookStatus.CHARGING.value],
         # unbook/stop is special and only permits when pile is locked/started
         # charging by current book
        'unbook': [],
        'stop': [],
        'cardstart': [],
        'cardstop': [],
    }
    def __init__(self):
        args = [ (Key.mobile, True, ArgType.STR, ""),
                 (Key.sn, True, ArgType.STR, ""),
                 (Key.book, True, ArgType.INT, 0),
                 (Key.action, True, ArgType.STR, ""),]
        self.arg_helper = JsonArgHelper(args)
        super(Permission, self).__init__()

    def start_by_card(self, pile):
        start_ts = datetime.utcnow()
        start = to_ts(start_ts)
        end = start + CARD_CHARGE_DURATION_SECONDS
        if pile.locked_by or pile.started_by:
            active_book_id = pile.locked_by if pile.locked_by else pile.started_by
            current_book = Book.query.get(active_book_id)
            app.logger.info(
                'found active book id %s, book %s, book.id %s',
                active_book_id, current_book, current_book.id if current_book else 'n/a'
            )
            if current_book and current_book.user_id == pile.owner_id:
                return ErrNo.OK
            else:
                return ErrNo.DUP
        ret, book, pts = create_book(pile.id, pile.owner_id, start, end)
        if ret != ErrNo.OK or not book or not send_mns_action(pile.sn, book.id, 'stop', delay=CARD_CHARGE_DURATION_SECONDS):
            app.logger.info('create book returned %s %s %s.', ret, book, pts)
            db.session.rollback()
            return ErrNo.DUP
        else:
            app.logger.info('create book %d for card charging %s.', book.id, book)
            book.status = BookStatus.CHARGING.value
            book.charge_start = start_ts

        try:
            db.session.flush()
            self.update_pile_usage(book, 'book')
            self.update_pile_usage(book, 'start')
            db.session.commit()
        except SQLAlchemyError as e:
            ret = ErrNo.DB
            app.logger.error('error happened in card start:')
            app.logger.exception(e)

        return ret

    def stop_by_card(self, pile):
        book = Book.query.filter(
            Book.user_id == pile.owner_id
        ).order_by(
            Book.id.desc()
        ).first()
        if not book or book.id not in (pile.locked_by, pile.started_by):
            self.log_refuse(pile.sn, 0, 'cardstop', 'not booked by owner.')
            if book:
                app.logger.info('book id %s, locked by %s, started by %s', book.id, pile.locked_by, pile.started_by)
            return ErrNo.INVALID
        if book.status != BookStatus.CHARGING.value:
            self.log_refuse(
                pile.sn, book.id, 'cardstop',
                'book of owner is not in charging state (now %s)'%(book.status, )
            )
            return ErrNo.INVALID
        self.update_owner_booking(book)
        db.session.flush()
        self.update_pile_usage(book, 'stop')
        db.session.commit()
        return ErrNo.OK

    def update_owner_booking(self, book):
        dt = datetime.utcnow()

        book.status = BookStatus.COMPLETE.value
        book.charge_end = dt
        if book.time_slot:
            book.time_slot.end = dt

    def log_refuse(self, sn, book_id, action, reason):
        app.logger.info('refused permission (%s, %s, %s), %s', book_id, sn, action, reason)

    def check_by_matrix(self, sn, book_id, action, status):
        matrix = self.permission_matrix.get(action)
        if matrix is None:
            self.log_refuse(sn, book_id, action, 'invalid action')
            return ErrNo.INVALID
        if matrix and status not in matrix:
            self.log_refuse(sn, book_id, action, 'invalid book status ' + str(status))
            return ErrNo.INVALID
        return ErrNo.OK

    def check_by_pile_usage(self, sn, book_id, action, pile):
        ret = ErrNo.OK
        if action in ['start', 'unbook',] and pile.locked_by != book_id:
            self.log_refuse(sn, book_id, action, 'not booked by me')
            ret = ErrNo.INVALID
        if action == 'stop' and pile.started_by != book_id:
            self.log_refuse(sn, book_id, action, 'not started by me')
            ret = ErrNo.INVALID
        return ret

    def update_pile_usage(self, book, action):
        if action == 'book':
            book.pile.locked_by = book.id
        elif action in ('unbook', 'stop'):
            book.pile.locked_by = None

        if action == 'start':
            book.pile.started_by = book.id
        elif action == 'stop':
            book.pile.started_by = None
            if book.pile.owner_id == book.user_id:
                self.update_owner_booking(book)
        app.logger.info('update pile usage, locked by %s, started by %s', book.pile.locked_by, book.pile.started_by)

    def handle_card_actions(self, action, pile):
        if action == 'cardstart':
            ret = self.start_by_card(pile)
        elif action == 'cardstop':
            ret = self.stop_by_card(pile)
        return result(ret)

    def post(self):
        ret = self.arg_helper.check()
        if ret != ErrNo.OK:
            return result(ret)
        mobile, sn, book_id, action = self.arg_helper.get_param_values()
        book = db.session.query(Book).get(book_id)
        pile = Pile.query.filter(Pile.sn == sn).first()
        app.logger.info('pile %s ask for permission: %s %s', sn, book_id, action)

        if action.startswith('card') and pile is None:
            self.log_refuse(sn, book_id, action, 'no such pile')
            return result(ErrNo.NOID)
        if action.startswith('card'):
            # return here because db session has been committed
            return self.handle_card_actions(action, pile)
        elif book is None:
            self.log_refuse(sn, book_id, action, 'no such book')
            return result(ErrNo.NOID)

        ret = self.check_by_matrix(sn, book_id, action, book.status)
        if ErrNo.OK != ret:
            return result(ret)

        ret = self.check_by_pile_usage(sn, book_id, action, book.pile)
        if ErrNo.OK != ret:
            return result(ret)

        self.update_pile_usage(book, action)
        if ret == ErrNo.OK:
            db.session.commit()

        app.logger.info('%s %s %s permitted', sn, book_id, action)
        return result(ErrNo.OK)

class GetPm25Stat(Resource):
    def __init__(self):
        arguments = [
            (Key.token, True, ArgType.STR, ""),
            (Key.type, False, ArgType.STR, "hour"),
            (Key.time, False, ArgType.INT, 0),
        ]
        self.arg_helper = JsonArgHelper(arguments)
        super(GetPm25Stat, self).__init__()

    def get_hour(self, time):
        hourly_pm = HourlyPm25.query.filter(
            HourlyPm25.hour == extract_hour_dt(time)
        ).order_by(
            HourlyPm25.hour.desc()
        ).limit(1).first()
        if not hourly_pm:
            return ErrNo.OK, None
        hour = hourly_pm.hour
        hourly_pm = hourly_pm.to_json()
        hourly_pm['detail'] = list()
        for ts, pm25 in TerminalInfo.query.with_entities(
            TerminalInfo.ts, TerminalInfo.info_pm25
        ).filter(
            TerminalInfo.ts >= hour,
            TerminalInfo.ts <= time
        ).order_by(TerminalInfo.ts.desc()).limit(30).all():
            hourly_pm['detail'].append({
                'time': to_ts(ts),
                'value': str(pm25),
            })
        return ErrNo.OK, hourly_pm

    def _get_day_stat(self, time, num):
        ans = []
        date = extract_date(time)
        week_data = DailyPm25.query.filter(
            DailyPm25.date <= date
        ).order_by(
            DailyPm25.date.desc()
        ).limit(num).all()
        for d in week_data:
            ans.append(d.to_json())

        return ErrNo.OK, ans

    def get_week(self, time):
        return self._get_day_stat(time, 7)

    def get_month(self, time):
        return self._get_day_stat(time, 30)

    def post(self):
        ret = self.arg_helper.check()
        if ret != ErrNo.OK:
            return result(ret)
        typ, time = self.arg_helper.get_param_values()
        if not time:
            time = datetime.utcnow()
        else:
            time = to_dt(time)

        cb = getattr(self, 'get_'+typ)
        if not cb or not callable(cb):
            return result(ErrNo.INVALID)
        ret, data = cb(time)

        return result(ret, data=data)

class TerminalImageLoad(Resource):
    def __init__(self):
        # index is used as hint to minimize data transmitting:
        # * if given, the latest image will be returned only when its version is
        #   higher than index
        # * if ommitted, the lates image will always be returned
        arguments = [
            (Key.index, False, ArgType.INT, 0),
        ]
        self.arg_helper = JsonArgHelper(arguments)
        super(TerminalImageLoad, self).__init__()

    def post(self):
        ret = self.arg_helper.check()
        if ret != ErrNo.OK:
            return result(ret)
        hint = self.arg_helper.get_param_values()
        app.logger.info('got hint %s', hint)
        if hint and TerminalImage.query.filter(TerminalImage.version > hint).count() <= 0:
            return result(ErrNo.OK)
        image = TerminalImage.query.filter(
            TerminalImage.version > hint
        ).order_by(
            TerminalImage.id.desc()
        ).limit(1).first()
        if image:
            return result(ErrNo.OK, image=image.to_dict())
        return result(ErrNo.NOID)


api.add_resource(RegTerm, '/v1/terminal/reg')
api.add_resource(NewTermInfo, '/v1/terminal/info/new')
api.add_resource(NewTermChargeStat, '/v1/terminal/run/new')
api.add_resource(Permission, '/v1/terminal/permission')
api.add_resource(GetPm25Stat, '/v1/terminal/pm25')
api.add_resource(TerminalImageLoad, '/v1/terminal/image/get')

