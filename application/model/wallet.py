from datetime import datetime
from .. import db
from .helper import to_ts


class Wallet(db.Model):
    """
    This class defines wallet structure.

    id : record id
    user_id : user id
    available : available account
    balance : balance account
    transactions : related transaction list
    """
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.ForeignKey("user.id"))
    available = db.Column(db.DECIMAL(10, 2))
    balance = db.Column(db.DECIMAL(10, 2))
    transactions = db.relationship('Transaction', backref='wallet', lazy='dynamic')

    def __init__(self, user_id, balance=0, available=0):
        self.user_id = user_id
        self.available = available
        self.balance = balance


class Transaction(db.Model):
    """
    This class defines transaction structure.

    id : record id
    wallet_id : wallet id
    book_id : book id
    type : transaction type
    dt : timestamp
    amount : the money spend or received
    account : account name
    status : transaction status
    usage : transaction usage
    """
    id = db.Column(db.Integer, primary_key=True)
    wallet_id = db.Column(db.ForeignKey('wallet.id'))
    book_id = db.Column(db.ForeignKey('book.id'))
    type = db.Column(db.Integer)
    dt = db.Column(db.DateTime)
    amount = db.Column(db.DECIMAL(10, 2))
    account = db.Column(db.String(64))
    status = db.Column(db.SmallInteger)  # 0 pending, 1 successful, 2 denied
    usage = db.Column(db.SmallInteger)

    def __init__(self, wallet_id, type, amount, account=None, book_id=None, usage=None, dt=None, status=0):
        self.wallet_id = wallet_id
        self.amount = amount
        self.dt = dt if dt else datetime.utcnow()
        self.type = type
        self.status = status
        self.account = account
        self.book_id = book_id
        self.usage = usage

    def to_json(self):
        attrs = ('id', 'type', 'amount', 'status')
        json = {attr: self.__getattribute__(attr) for attr in attrs}
        if self.account is not None:
            json['account'] = self.account
        if self.book_id is not None:
            json['book_id'] = self.book_id
        if self.usage is not None:
            json['usage'] = self.usage
        json['dt'] = to_ts(self.dt)
        return json


