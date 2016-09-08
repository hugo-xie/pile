from .. import db, app
from .helper import to_ts
from ..const import BookStatus, ADJOIN_BOOK_SPACE_SECONDS
from .terminal import TerminalChargeStatus
from datetime import datetime, timedelta
from decimal import Decimal


class Book(db.Model):
    """
    This class defines book structure.

    id : record id
    user_id : user id
    pile_id : pile id
    book_start : book start time
    book_end : book end time
    charge_start : charge start time
    charge_end : charge end time
    electricity : electricity fee
    service : service fee
    appointment : appointment fee
    status : book status
    charged_value_base : <TODO>
    time_slot_id : time slot id

    """
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    pile_id = db.Column(db.Integer, db.ForeignKey('pile.id'))
    book_start = db.Column(db.DateTime, nullable=False)
    book_end = db.Column(db.DateTime, nullable=False)
    charge_start = db.Column(db.DateTime)
    charge_end = db.Column(db.DateTime)
    electricity = db.Column(db.Numeric(10, 2), nullable=False)
    service = db.Column(db.Numeric(10, 2), nullable=False)
    appointment = db.Column(db.Numeric(10, 2), nullable=False)
    status = db.Column(db.SmallInteger, nullable=False)
    charged_value_base = db.Column(db.DECIMAL(8, 2))
    time_slot_id = db.Column(db.Integer, db.ForeignKey('pile_time_slot.id'))

    def __init__(
            self, user_id, pile_id, book_start, book_end,
            electricity, service, appointment,
            time_slot_id,
            status=BookStatus.NPAID.value,
    ):
        self.user_id = user_id
        self.pile_id = pile_id
        self.book_start = book_start
        self.book_end = book_end
        self.status = status
        self.electricity = electricity
        self.service = service
        self.appointment = appointment
        self.time_slot_id = time_slot_id
        self.status = status
        self.charged_value_base = Decimal(0)

    def to_json(self, with_stat=False):
        attrs = ('id', 'user_id', 'pile_id', 'electricity', 'service', 'appointment', 'status')
        json = {attr: self.__getattribute__(attr) for attr in attrs}
        json['book_start'] = to_ts(self.book_start)
        json['book_end'] = to_ts(self.book_end)
        json['ano_book_start'] = self.book_start.strftime('%Y-%m-%d %H:%M:%S')
        json['ano_book_end'] = self.book_end.strftime('%Y-%m-%d %H:%M:%S')
        json['user'] = {'name': self.user.name}
        if hasattr(self.pile, "name"):  # ½öÐÞ¸´bug
            json['pile'] = {'name': self.pile.name}
        else:
            json['pile'] = {'name': None}
        if self.charge_start is not None:
            json['charge_start'] = to_ts(self.charge_start)
        else:
            json['charge_start'] = 0
        if self.charge_end is not None:
            json['charge_end'] = to_ts(self.charge_end)
        else:
            json['charge_end'] = 0
        if with_stat and self.status in (
                BookStatus.CHARGING.value, BookStatus.COMPLETE.value
        ) and self.charge_start:
            end = self.charge_end if self.charge_end else datetime.utcnow()
            stat = TerminalChargeStatus.query.filter(
                TerminalChargeStatus.sn == self.pile.sn,
                TerminalChargeStatus.ts >= self.charge_start,
                TerminalChargeStatus.ts <= end,
            ) \
                .order_by(TerminalChargeStatus.ts.desc()) \
                .first()
            stat_json = json.setdefault('stat', dict())
            stat_json['total'] = min([
                int(
                    (self.book_end - self.charge_start).total_seconds()
                ),
                int(
                    (self.book_end - self.book_start).total_seconds()
                ),
            ])
            if stat:
                stat_json['duration'] = stat.info_duration * 60
                stat_json['charged'] = stat.info_charged - self.charged_value_base
                if stat_json['charged'] < 0:
                    stat_json['charged'] += 65536
                stat_json['charged'] = str(stat_json['charged'])
                stat_json['current'] = str(stat.info_current)
                stat_json['voltage'] = str(stat.info_volt)
            else:
                stat_json['duration'] = 0
                stat_json['charged'] = '0.00'
                stat_json['current'] = '0.00'
                stat_json['voltage'] = '0.00'

            if self.charge_end:
                # charging is completed
                stat_json['remain'] = 0
            else:
                if stat_json['total'] > stat_json['duration']:
                    stat_json['remain'] = stat_json['total'] - stat_json['duration']
                else:
                    stat_json['remain'] = 0
        return json

    def in_charge_window(self, now=None):
        if not now:
            now = datetime.utcnow()
        reservation_end_dt = now - timedelta(0, ADJOIN_BOOK_SPACE_SECONDS)
        reservation_start_dt = now + timedelta(0, ADJOIN_BOOK_SPACE_SECONDS)
        return reservation_start_dt >= self.book_start and reservation_end_dt < self.book_end

    def still_on_time(self, now=None):
        if not now:
            now = datetime.utcnow()
        reservation_start_dt = now + timedelta(0, ADJOIN_BOOK_SPACE_SECONDS)
        reservation_end_dt = now - timedelta(0, ADJOIN_BOOK_SPACE_SECONDS)
        if Book.query.filter(
                        Book.status == BookStatus.CHARGING.value,
                        Book.book_start <= reservation_end_dt,
                        Book.book_end >= reservation_start_dt
        ).count() > 0:
            app.logger.info('other overlapping book has been started, cannot handle %s', self.id)
            return False
        return reservation_end_dt < self.book_end
