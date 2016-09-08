from flask_restful import Resource
from sqlalchemy.exc import SQLAlchemyError
from .keys import Key
from .helper import ArgType, JsonArgHelper
from ..model.wallet import Transaction, Wallet
from .. import api, db, app
from ..const import ErrNo, result, TransType
from .book_state_machine import on_topup


class Transactions(Resource):
    """
    This class returns corresponding transaction list.
    Parameters:
        token: token get from Login function
        index: the first transaction id user wants to search
        count: the count of transactions user wants to search
    Error:
        PARAM: invalid parameter of user input
        DB: database operation failure
        TOKEN: token invalid
    """
    def __init__(self):
        arguments = [(Key.token, True, ArgType.STR, ''),
                     (Key.index, False, ArgType.INT, 0),
                     (Key.count, False, ArgType.INT, 50)]
        self.arg_helper = JsonArgHelper(arguments)
        super(Transactions, self).__init__()

    def post(self):
        ret = self.arg_helper.check()
        if ret != ErrNo.OK:
            return result(ret)

        user = self.arg_helper.get_user()
        index, count = self.arg_helper.get_param_values()
        if index < 0:
            # make an always true condition
            index_filter = (Transaction.id >= 0)
        else:
            index_filter = (Transaction.id <= index)
        try:
            if user.wallet is None:
                return result(ErrNo.OK, count=0, index=-1, transactions=[])
            transactions = db.session.query(Transaction).filter(Transaction.wallet_id == user.wallet.id,
                                                                index_filter).order_by(Transaction.id.desc()).\
                limit(count).all()
            count = len(transactions)
            if count > 0:
                last_index = transactions[-1].id - 1
            else:
                last_index = 0
            return result(ErrNo.OK, count=count, index=last_index, transactions=[t.to_json() for t in transactions])
        except SQLAlchemyError as e:
            app.logger.exception(e)
            msg = str(e)
            return result(ErrNo.DB, msg=msg)


class Withdraw(Resource):
    """
    This class handles user's withdraw application, it will update user's account status
    and record corresponding transactions.
    Parameters:
        token: token get from Login function
        money: the mount of money user wants to withdraw
        account: user's alipay account
    Errors:
        PARAM: invalid parameter of user input
        INVALID: the money exceeds available account
        DB: database operation failure
        TOKEN: token invalid
    """
    def __init__(self):
        arguments = [(Key.token, True, ArgType.STR, ''),
                     (Key.money, True, ArgType.DECIMAL, 0),
                     (Key.account, True, ArgType.STR, 0)]
        self.arg_helper = JsonArgHelper(arguments)
        super(Withdraw, self).__init__()

    def post(self):
        ret = self.arg_helper.check()
        if ret != ErrNo.OK:
            return result(ret)
        user = self.arg_helper.get_user()
        money, account = self.arg_helper.get_param_values()
        try:
            if user.wallet is None:
                wallet = Wallet(user.id)
                db.session.add(wallet)
                db.session.commit()
            if money > user.wallet.available:
                return result(ErrNo.INVALID)
            trans = Transaction(user.wallet.id, TransType.WITHDRAW.value, money, account)
            db.session.add(trans)
            user.wallet.available -= money
            db.session.commit()
            return result(ErrNo.OK, id=trans.id)
        except SQLAlchemyError as e:
            app.logger.exception(e)
            msg = str(e)
            return result(ErrNo.DB, msg=msg)


class Topup(Resource):
    """
    This class handles user's topup application, it will update user's account status
    and record corresponding transactions.
    Parameters:
        token: token get from Login function
        money: the mount of money user wants to withdraw
        account: user's alipay account
    Errors:
        PARAM: invalid parameter of user input
        DB: database operation failure
        TOKEN: token invalid
    """
    def __init__(self):
        arguments = [(Key.token, True, ArgType.STR, ''),
                     (Key.money, True, ArgType.DECIMAL, 0),
                     (Key.account, True, ArgType.STR, 0)]
        self.arg_helper = JsonArgHelper(arguments)
        super(Topup, self).__init__()

    def post(self):
        ret = self.arg_helper.check()
        if ret != ErrNo.OK:
            return result(ret)
        user = self.arg_helper.get_user()
        money, account = self.arg_helper.get_param_values()
        try:
            trans = on_topup(user, money, account)
            db.session.commit()
            return result(ErrNo.OK, id=trans.id)
        except SQLAlchemyError as e:
            app.logger.exception(e)
            msg = str(e)
            return result(ErrNo.DB, msg=msg)


api.add_resource(Transactions, '/v1/wallet/transactions')
api.add_resource(Withdraw, '/v1/wallet/withdraw')
api.add_resource(Topup, '/v1/wallet/topup')
