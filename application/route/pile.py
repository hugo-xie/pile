from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy import and_, func
from flask_restful import Resource
from datetime import datetime
from .. import api, app
from ..model.book import Book
from ..model.pile import Pile
from ..model.pile_time_slot import PileTimeSlot
from ..model.helper import to_dt
from ..const import ADJOIN_BOOK_SPACE_SECONDS, ErrNo, result
from .helper import ArgType, JsonArgHelper
from .keys import Key
from application import db


class SearchPile(Resource):
    """
    This class handles "Search Pile" function, it will return a list of Pile object, the count of the list, index for
    next search if it is invoked successfully.

    The parameters include:
        llong	指定范围左边维度
        rlong	指定范围右边维度
        ulat	指定范围上方经度
        blat	指定范围下方经度
        index   从该充电桩ID开始寻找
        count   返回充电桩的数量，默认50个

    The error it may return includes:
        PARAM: invalid parameter of user input
        DB: database operation failure

    """
    def __init__(self):
        arguments = [(Key.llong, True, ArgType.FLOAT, ''),
                     (Key.rlong, True, ArgType.FLOAT, ''),
                     (Key.ulat, True, ArgType.FLOAT, ''),
                     (Key.blat, True, ArgType.FLOAT, ''),
                     (Key.index, False, ArgType.INT, 0),
                     (Key.count, False, ArgType.INT, 50),
                     (Key.starttime, False, ArgType.INT, 0)]
        self.arg_helper = JsonArgHelper(arguments)
        super(SearchPile, self).__init__()

    def post(self):
        ret = self.arg_helper.check()
        if ret != ErrNo.OK:
            return result(ret)
        llong, rlong, ulat, blat, index, count, starttime = self.arg_helper.get_param_values()
        try:
            piles_query = Pile.query.filter(Pile.latitude <= ulat,
                                      Pile.latitude >= blat,
                                      Pile.longitude <= rlong,
                                      Pile.longitude >= llong,
                                      Pile.id >= index)
            if starttime:
                # for a given starttime, it is reservable only when previous time
                # slot ends at least X seconds before it, and the next time
                # slot starts at least X seconds after it, X is the designed
                # gap between each two adjoined bookings
                reservation_start_dt = datetime.utcfromtimestamp(starttime+ADJOIN_BOOK_SPACE_SECONDS)
                reservation_end_dt = datetime.utcfromtimestamp(starttime-ADJOIN_BOOK_SPACE_SECONDS)
                piles_query = piles_query.filter(
                    ~Pile.time_slots.any(and_(
                       PileTimeSlot.start <= reservation_start_dt,
                       PileTimeSlot.end > reservation_end_dt
                    ))
                )
            piles = piles_query.order_by(Pile.id).limit(count).all()
            count = len(piles)
            if count > 0:
                last_index = piles[-1].id + 1
            else:
                last_index = -1
            return result(ErrNo.OK, count=count, index=last_index, piles=[pile.to_json() for pile in piles])
        except SQLAlchemyError as e:
            return result(ErrNo.DB, msg=str(e))


class GetPileInfo(Resource):
    """
    This class handles "Get Pile Information" function, it will return Pile object when invoked successfully.

    Parameters:
        id: pile id

    Errors:
        PARAM: invalid parameter of user input
        DB: database operation failure
    """
    def __init__(self):
        arguments = [(Key.id, True, ArgType.INT, '')]
        self.arg_helper = JsonArgHelper(arguments)
        super(GetPileInfo, self).__init__()

    def post(self):
        ret = self.arg_helper.check()
        if ret != ErrNo.OK:
            return result(ret)
        id = self.arg_helper.get_param_values()
        try:
            pile = Pile.query.get(id)
        except SQLAlchemyError as e:
            return result(ErrNo.DB, msg=str(e))
        if pile is None:
            return result(ErrNo.NOID)
        return result(ErrNo.OK, pile=pile.to_json())


class GetPileList(Resource):
    def __init__(self):
        arguments = [(Key.token, True, ArgType.STR, '')]
        self.arg_helper = JsonArgHelper(arguments)
        super(GetPileList, self).__init__()

    def post(self):
        ret = self.arg_helper.check()
        if ret != ErrNo.OK:
            return result(ret)
        user = self.arg_helper.get_user()
        try:
            piles = db.session.query(Pile).filter(Pile.owner_id==user.id).all()
            return result(ErrNo.OK, list=[pile.to_json() for pile in piles])
        except SQLAlchemyError as e:
            return result(ErrNo.DB, msg=str(e))


class UpdatePile(Resource):
    """
    This class handles "Update Pile Information" function, it will return the result of update.

    Parameters:
        id: pile id
        name: pile name
        service: service fee
        electricity: electricity fee
        appointment: appointment fee
        open: open time (datetime)
        close: close time (datetime)
        auto_ack: automatically acknowledge
        auto_ack_start: automatically acknowledge start time
        auto_ack_end: automatically acknowledge end time

    Errors:
        PARAM: invalid parameter of user input
        DB: database operation failure
        NOID: cannot find pile according to id
        NOAUTH: is not the owner of the pile
    """
    def __init__(self):
        arguments = [(Key.token, True, ArgType.STR, ''),
                     (Key.id, True, ArgType.STR, ''),
                     (Key.name, False, ArgType.STR, ''),
                     (Key.service, False, ArgType.DECIMAL, -1.0),
                     (Key.electricity, False, ArgType.DECIMAL, -1.0),
                     (Key.appointment, False, ArgType.DECIMAL, -1.0),
                     (Key.open, False, ArgType.INT, -1),
                     (Key.close, False, ArgType.INT, -1),
                     (Key.auto_ack, False, ArgType.INT, -1),
                     (Key.auto_ack_start, False, ArgType.INT, -1),
                     (Key.auto_ack_end, False, ArgType.INT, -1)]
        self.arg_helper = JsonArgHelper(arguments)
        super(UpdatePile, self).__init__()

    def post(self):
        ret = self.arg_helper.check()
        if ret != ErrNo.OK:
            return result(ret)
        id, name, service, electricity, appointment, open, close, auto_ack, auto_ack_start, auto_ack_end = \
            self.arg_helper.get_param_values()
        if auto_ack > 0 and (auto_ack_start < 0 or auto_ack_end < 0):
            return result(ErrNo.PARAM)

        pile = db.session.query(Pile).get(id)
        if pile is None:
            return result(ErrNo.NOID)

        if pile.owner_id != self.arg_helper.get_user().id:
            return result(ErrNo.NOAUTH)

        if name != '':
            pile.name = name
        if service >= 0.0:
            pile.service = service
        if electricity >= 0.0:
            pile.electricity = electricity
        if appointment >= 0.0:
            pile.appointment = appointment
        if open >= 0:
            pile.open = to_dt(open).time()
        if close >= 0:
            pile.close = to_dt(close).time()
        if auto_ack != -1:
            pile.auto_ack = auto_ack
        if auto_ack_start >= 0:
            pile.auto_ack_start = to_dt(auto_ack_start)
        if auto_ack_end >= 0:
            pile.auto_ack_end = to_dt(auto_ack_end)
        try:
            db.session.commit()
        except SQLAlchemyError as e:
            app.logger.exception(e)
            return result(ErrNo.DB)
        return result(ErrNo.OK)


class FavoritePile(Resource):
    """
    This class returns user's latest used 10 piles.
    Parameters:
        token: token get from Login function
    Errors:
        PARAM: invalid parameter of user input
        DB: database operation failure
        TOKEN: token invalid
    """
    def __init__(self):
        arguments = [(Key.token, True, ArgType.STR, '')]
        self.arg_helper = JsonArgHelper(arguments)
        super(FavoritePile, self).__init__()

    def post(self):
        ret = self.arg_helper.check()
        if ret != ErrNo.OK:
            return result(ret)
        user = self.arg_helper.get_user()
        try:
            my_latest_100_book_id = Book.query.with_entities(
                Book.id
            ).filter(
                Book.user_id == user.id
            ).order_by(
                Book.id.desc()
            ).limit(100)
            # mysql doesn't support limit subquery, have to turn it into
            # python list
            book_ids = [r[0] for r in my_latest_100_book_id.all()]
            favorite_pile_ids = Book.query.with_entities(
                Book.pile_id, func.count(Book.id)
            ).filter(
                Book.id.in_(book_ids)
            ).group_by(
                Book.pile_id
            ).order_by(
                func.count(Book.id).desc()
            ).limit(10).all()
            favorite_pile_ids = dict(favorite_pile_ids)

            favorite_piles = Pile.query.filter(
                Pile.id.in_(list(favorite_pile_ids.keys()))
            )
            piles = [pile.to_json() for pile in favorite_piles.all()]
            for p in piles:
                p['books_count'] = favorite_pile_ids.get(p['id'], 0)
            piles = sorted(piles, key=lambda p: p['books_count'], reverse=True)

            return result(ErrNo.OK, piles=piles)
        except SQLAlchemyError as e:
            return result(ErrNo.DB, msg=str(e))


api.add_resource(SearchPile, '/v1/piles/search')
api.add_resource(GetPileInfo, '/v1/piles/info')
api.add_resource(GetPileList, '/v1/piles/list')
api.add_resource(UpdatePile, '/v1/piles/update')
api.add_resource(FavoritePile, '/v1/piles/favorite')
