from decimal import Decimal
from datetime import datetime
from .helper import send_mns_action
from .. import db, app
from ..model.wallet import Transaction
from ..model.friend import Friend
from ..model.helper import to_ts
from ..const import result, ErrNo, TransType, TransUsage, TransStatue, BookStatus, ADJOIN_BOOK_SPACE_SECONDS

def show_balance(promt, wallet):
    print(promt)
    print("Available: %f" % wallet.available)
    print("Balance: %f" % wallet.balance)

def cal_appointment_fee(book):
    """
    This function calculates appointment fee, which depends on book duration.
    :param book: book object
    :return: appointment fee
    """
    duration = (book.book_end - book.book_start).total_seconds() / 3600.0
    if duration <= 1.0:
        multiple = 1
    elif duration <= 3.0:
        multiple = 2
    else:
        multiple = 4
    return round(book.appointment * multiple, 0)

def cal_service_fee(book):
    """
    This function calculates service fee with electricity fee added.
    :param book: book object
    :return: service fee with electricity fee added.
    """
    duration = book.book_end - book.book_start
    return round(book.service + book.electricity * Decimal(duration.total_seconds()) / 3600, 0)


def handle_auto_accept(book):
    """
    This function accept the book automatically, if the book status is proper and its
    time window is inside the automatically acknowledge time window set by the pile
    owner.
    :param book: book object
    :return: result, book id, book status
    """
    ret = ErrNo.OK
    db.session.flush()
    pile = book.pile
    if not pile.auto_ack or pile.auto_ack_start is None or pile.auto_ack_end is None:
        return ret, book.id, book.status

    app.logger.info(
        'book start time %s, ack start time %s, book stop time %s, ack end time %s',
         book.book_start.time(), pile.auto_ack_start.time(),
            book.book_end.time(), pile.auto_ack_end.time()
    )
    if book.book_start.time() >= pile.auto_ack_start.time() and \
        book.book_end.time() < pile.auto_ack_end.time():
            app.logger.info('auto accept enabled and fits book, accept it')
            ret = on_accept(book)
    if ret != ErrNo.OK:
        app.logger.error('auto accept returns error %s', ret)
    return ret, book.id, book.status


def on_topup(user, money, account):
    """
    This function tops up the user's account, and records corresponding transactions.
    :param user: user object
    :param money: the amount of money
    :param account: account object
    :return: the transaction object
    """
    trans = Transaction(user.wallet.id, TransType.TOPUP.value, money, account=account,
                        status=TransStatue.SUCCESS.value)
    user.wallet.balance += money
    user.wallet.available += money
    db.session.add(trans)
    if app.debug:
        show_balance('Topup', user.wallet)
    return trans


def on_pay(book):
    """
    This functions is used for pile applicant to pay pile owner fees including service
    fee and appointment fee (electricity fee included). The fees will be deducted
    from the applicant's available account and transferred to the owner's balance
    account. This function updates both users' wallet and records corresponding
    transactions.
    :param
        book: book object
    :return:
        result:
            INVALID: corresponding transaction record missing
            OK
        book id: the id of the book
        book status: the status of the book
    """
    service = cal_service_fee(book)
    appointment = cal_appointment_fee(book)
    cost = service + appointment
    # User's wallet
    wallet = book.user.wallet
    if cost > book.user.wallet.available:
        book.status = BookStatus.NPAID.value
        return ErrNo.OK, book.id, book.status
        #return result(ErrNo.NOMONEY, money=cost-wallet.available, id=book.id)
    book.status = BookStatus.PAID.value
    trans = Transaction(wallet.id, TransType.PAY.value, appointment, book_id=book.id,
                        usage=TransUsage.APPOINTMENT.value)
    db.session.add(trans)
    trans = Transaction(wallet.id, TransType.PAY.value, service, book_id=book.id,
                        usage=TransUsage.SERVICE.value)
    db.session.add(trans)
    wallet.available -= cost
    if app.debug:
        show_balance('Booker', wallet)


    # Pile owner's wallet
    wallet = book.pile.user.wallet
    trans = Transaction(wallet.id, TransType.RECEIVE.value, appointment, book_id=book.id,
                        usage=TransUsage.APPOINTMENT.value)
    db.session.add(trans)
    trans = Transaction(wallet.id, TransType.RECEIVE.value, service, book_id=book.id,
                        usage=TransUsage.SERVICE.value)
    db.session.add(trans)
    wallet.balance += cost
    if app.debug:
        show_balance('Owner', wallet)

    friend = db.session.query(Friend).filter(
        Friend.user_id == book.pile.owner_id,
        Friend.friend_id == book.user.id).first()
    if friend is not None:
        ret = on_accept(book)
    else:
        ret, bookid, bookstatus = handle_auto_accept(book)
    return ret, book.id, book.status


def on_accept(book):
    """
    This function is used for the pile owner to accept the applicant's pay. The fees will
    be added to the owner's available account (with commission fee deducted) and reduced
    from the applicant's balance account. This function updates both sides' wallet, draws
    commission fee, and records transactions.
    :param
        book: book object
    :return:
        result:
            INVALID: corresponding transaction record missing
            OK
    """
    book.status = BookStatus.ACCEPT.value
    wallet1 = book.user.wallet
    wallet2 = book.pile.user.wallet
    trans = db.session.query(Transaction).filter(Transaction.wallet_id == wallet1.id,
                                                 Transaction.type == TransType.PAY.value,
                                                 Transaction.book_id == book.id,
                                                 Transaction.usage == TransUsage.APPOINTMENT.value).first()
    if trans is None:
        app.logger.warn('a. no trans found')
        return ErrNo.INVALID
    trans.status = TransStatue.SUCCESS.value
    wallet1.balance -= trans.amount
    book.user.statistic.cost += trans.amount
    trans = db.session.query(Transaction).filter(Transaction.wallet_id == wallet2.id,
                                                 Transaction.type == TransType.RECEIVE.value,
                                                 Transaction.book_id == book.id,
                                                 Transaction.usage == TransUsage.APPOINTMENT.value).first()
    if trans is None:
        app.logger.warn('b. no trans found')
        return ErrNo.INVALID
    trans.status = TransStatue.SUCCESS.value
    if app.debug:
        show_balance('Booker', wallet1)

    commission = round(trans.amount * Decimal(0.02))
    benefit = trans.amount - commission
    wallet2.available += benefit
    wallet2.balance -= commission
    book.pile.user.statistic.profit += benefit
    if app.debug:
        show_balance('Owner', wallet2)

    trans = Transaction(wallet2.id, TransType.PAY.value, commission, book_id=book.id,
                        usage=TransUsage.COMMISSION.value)
    db.session.add(trans)
    now_dt = datetime.utcnow()
    reservation_start_dt = datetime.utcfromtimestamp(to_ts(book.book_start) - ADJOIN_BOOK_SPACE_SECONDS)
    if reservation_start_dt > now_dt:
        delay = int((reservation_start_dt - now_dt).total_seconds())
    else:
        # add a short delay to make sure db operations are settled
        delay = 1
    app.logger.debug('send book msg book id %s to queue %s', book.id, book.pile.sn)
    if not send_mns_action(book.pile.sn, book.id, 'book', delay=delay):
        app.logger.debug('mns message not sent')
        return ErrNo.MNS
    delay = int((book.book_end - now_dt).total_seconds())
    send_mns_action(book.pile.sn, book.id, 'unbook', delay=delay)
    return ErrNo.OK

def on_decline(book):
    """
    This function is used for the pile owner to reject the applicant's pay. The money
    will be returned back, both sides' wallet will be rolled back, and the transaction
    record will be updated.
    :param
        book: book object
    :return:
        result:
            INVALID: corresponding transaction record missing
            OK
    """
    book.status = BookStatus.DECLINE.value
    wallet1 = book.user.wallet
    wallet2 = book.pile.user.wallet
    trans = db.session.query(Transaction).filter(Transaction.wallet_id == wallet1.id,
                                                 Transaction.type == TransType.PAY.value,
                                                 Transaction.book_id == book.id).all()
    if len(trans) != 2:
        return ErrNo.INVALID

    for t in trans:
        t.status = TransStatue.FAIL.value
        wallet1.available += t.amount
    if app.debug:
        show_balance('Booker', wallet1)

    trans = db.session.query(Transaction).filter(Transaction.wallet_id == wallet2.id,
                                                 Transaction.type == TransType.RECEIVE.value,
                                                 Transaction.book_id == book.id).all()
    if len(trans) != 2:
        return ErrNo.INVALID

    for t in trans:
        t.status = TransStatue.FAIL.value
        wallet2.balance -= t.amount
    if app.debug:
        show_balance('Owner', wallet2)
    return ErrNo.OK


def on_stop_charge(book):
    """
    This function is used for the applicant to stop recharging and pay real incurred
    fees which depends on real recharging duration. Both sides' wallet will be updated,
    and corresponding transactions will be recorded.
    :param
        book: book object
    :return:
        result:
            INVALID: corresponding transaction record missing
            OK
    """
    duration = book.charge_end - book.charge_start
    cost = round(book.service + book.electricity * Decimal(duration.total_seconds() / 3600), 0)
    wallet1 = book.user.wallet
    wallet2 = book.pile.user.wallet
    trans = db.session.query(Transaction).filter(Transaction.wallet_id == wallet1.id,
                                                 Transaction.type == TransType.PAY.value,
                                                 Transaction.book_id == book.id,
                                                 Transaction.usage == TransUsage.SERVICE.value).first()
    if trans is None:
        return ErrNo.INVALID
    if cost == trans.amount:
        trans.status = TransStatue.SUCCESS.value
    else:
        trans.status = TransStatue.FAIL.value
        wallet1.available += trans.amount
        trans = Transaction(wallet1.id, TransType.PAY.value, cost, book_id=book.id,
                            usage=TransUsage.SERVICE.value, status=TransStatue.SUCCESS.value)
        wallet1.available -= cost
        db.session.add(trans)
    wallet1.balance -= cost
    book.user.statistic.cost += cost
    if app.debug:
        show_balance('Booker', wallet1)
    trans = db.session.query(Transaction).filter(Transaction.wallet_id == wallet2.id,
                                                 Transaction.type == TransType.RECEIVE.value,
                                                 Transaction.book_id == book.id,
                                                 Transaction.usage == TransUsage.SERVICE.value).first()

    if trans is None:
        return ErrNo.INVALID
    if cost == trans.amount:
        trans.status = TransStatue.SUCCESS.value
    else:
        trans.status = TransStatue.FAIL.value
        wallet2.balance -= trans.amount
        trans = Transaction(wallet2.id, TransType.RECEIVE.value, cost, book_id=book.id,
                            usage=TransUsage.SERVICE.value, status=TransStatue.SUCCESS.value)
        db.session.add(trans)
    commission = round(cost * Decimal(0.02))
    benefit = cost - commission
    wallet2.available += benefit
    wallet2.balance += benefit
    if app.debug:
        show_balance('Owner', wallet2)
    book.pile.user.statistic.profit += benefit
    trans = Transaction(wallet2.id, TransType.PAY.value, commission, book_id=book.id,
                        usage=TransUsage.COMMISSION.value, status=TransStatue.SUCCESS.value)
    db.session.add(trans)
    return ErrNo.OK


def on_cancel(book):
    """
    This function is used for the applicant to cancel the book. Both sides' wallets will
    be updated and corresponding transaction status will be updated.
    :param
        book: book object
    :return:
        result:
            INVALID: corresponding transaction record missing
            OK
    """
    wallet1 = book.user.wallet
    wallet2 = book.pile.user.wallet
    trans = db.session.query(Transaction).filter(Transaction.wallet_id == wallet1.id,
                                                 Transaction.type == TransType.PAY.value,
                                                 Transaction.book_id == book.id,
                                                 Transaction.usage == TransUsage.SERVICE.value).first()
    if trans is None:
        return result(ErrNo.INVALID)
    trans.status = TransStatue.FAIL.value
    wallet1.available += trans.amount
    if app.debug:
        show_balance('User', wallet1)
    trans = db.session.query(Transaction).filter(Transaction.wallet_id == wallet2.id,
                                                 Transaction.type == TransType.RECEIVE.value,
                                                 Transaction.book_id == book.id,
                                                 Transaction.usage == TransUsage.SERVICE.value).first()
    if trans is None:
        return ErrNo.INVALID
    trans.status = TransStatue.FAIL.value
    wallet2.balance -= trans.amount
    if app.debug:
        show_balance('Owner', wallet2)
    return ErrNo.OK

