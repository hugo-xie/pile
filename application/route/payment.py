from decimal import Decimal
from flask_restful import Resource
from sqlalchemy.exc import SQLAlchemyError
from .keys import Key
from .helper import ArgType, JsonArgHelper
from ..model.book import Book
from .. import api, db
from ..const import BookStatus, ErrNo, result
from .book_state_machine import on_pay, on_topup


class Pay(Resource):
    """
    This class handles "Pay" function, it checks order and money on 3rd payment website.

    Parameters:
        token: token get from Login
        order: order id
        money: money user paid

    Errors:
        PARAM: invalid parameter of user input
        DB: database operation failure
        TOKEN: token invalid
        INVALID: invalid payment
    """
    def __init__(self):
        arguments = [(Key.token, True, ArgType.STR, ''),
                     #(Key.book, True, ArgType.INT, '')]
                     (Key.id, True, ArgType.INT, ''), # FIXME book id, mock for debug usage, remove after alipay API integrated
                     (Key.money, True, ArgType.FLOAT, '')]
        self.arg_helper = JsonArgHelper(arguments)
        super(Pay, self).__init__()

    def post(self):
        ret = self.arg_helper.check()
        if ret != ErrNo.OK:
            return result(ret)
        book_id, money = self.arg_helper.get_param_values()
        user = self.arg_helper.get_user()
        try:
            on_topup(user, Decimal(money), 'mockalipay')
            book = db.session.query(Book).get(book_id)
            if book.user_id != user.id:
                return result(ErrNo.NOAUTH)
            if book.status != BookStatus.NPAID.value:
                return result(ErrNo.INVALID)
            if book is None:
                return result(ErrNo.NOID)
            ret, bookid, bookstatus = on_pay(book)
            db.session.commit()
            return result(ret, id=bookid, status=bookstatus)
        except SQLAlchemyError as e:
            return result(ErrNo.DB, msg=str(e))

api.add_resource(Pay, '/v1/payment/pay')
