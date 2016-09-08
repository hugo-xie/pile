from flask import jsonify, request, url_for
from ..const import FLASKY_POSTS_PER_PAGE, permissionDenied, BookStatus
from ..route.helper import send_mns_action
from .role_auth_check import admin_auth, user_auth, maintainer_auth, merchant_auth, get_user
from .. import db
from ..model.book import Book
from ..model.pile import Pile
from . import api_bluePrint

from datetime import datetime


# book management
@api_bluePrint.route("/book/list", methods=['GET', 'POST'])
def get_books():
    user = get_user()
    merchant_id = None

    permission = False
    if admin_auth():
        merchant_id = None
        permission = True
    else:
        if merchant_auth():
            if user:
                merchant_id = user.id
            permission = True

    if not permission:
        return permissionDenied()

    page = request.args.get('offset', 1, type=int)
    per_page = request.args.get('limit', FLASKY_POSTS_PER_PAGE, type=int)
    order = request.args.get('order', 'asc', type=str)
    book_start_start = request.args.get('book_start_start', "", type=str)
    book_start_end = request.args.get('book_start_end', "", type=str)

    book_end_start = request.args.get('book_end_start', "", type=str)
    book_end_end = request.args.get('book_end_end', "", type=str)

    id = request.args.get('id', None, type=int)
    pile_sn = request.args.get('sn', None, type=str)  # 电桩sn查询
    pile_id = request.args.get('pile_id', None, type=int)  # 电桩id查询
    user_id = request.args.get('user_id', None, type=int)  # 用户id查询

    pagination = Book.query
    if book_start_start:
        # book_start_start = datetime.strptime(book_start_start, '%Y-%m-%d %H:%M:%S')
        book_start_start = datetime.strptime(book_start_start, '%Y-%m-%d')
        pagination = Book.query.filter(Book.book_start >= book_start_start)
    if book_start_end:
        # book_start_end = datetime.strptime(book_start_end, '%Y-%m-%d %H:%M:%S')
        book_start_end = datetime.strptime(book_start_end, '%Y-%m-%d')
        pagination = pagination.filter(Book.book_start < book_start_end)

    if book_end_start:
        # book_end_start = datetime.strptime(book_end_start, '%Y-%m-%d %H:%M:%S')
        book_end_start = datetime.strptime(book_end_start, '%Y-%m-%d')
        pagination = pagination.filter(Book.book_start >= book_end_start)
    if book_end_end:
        # book_end_end = datetime.strptime(book_end_end, '%Y-%m-%d %H:%M:%S')
        book_end_end = datetime.strptime(book_end_end, '%Y-%m-%d')
        pagination = pagination.filter(Book.book_start < book_end_end)

    if id:
        pagination = pagination.filter(Book.id == id)
    if pile_id:
        pagination = pagination.filter(Book.pile_id == pile_id)
    if merchant_id:
        pagination = pagination.filter(Book.user_id == merchant_id)
    if user_id:
        pagination = pagination.filter(Book.user_id == user_id)
    if pile_sn:
        pile = Pile.query.filter(Pile.sn == pile_sn).first()
        pagination = pagination.filter_by(pile=pile)

    pagination = pagination.paginate(page, per_page=per_page, error_out=False)

    books = pagination.items

    prev = None
    if pagination.has_prev:
        prev = url_for('api.get_books', offset=page - 1, _external=True)
    next = None
    if pagination.has_next:
        next = url_for('api.get_books', offset=page + 1, _external=True)
    return jsonify({
        'total': pagination.total,
        'rows': [book.to_json() for book in books]
    })


@api_bluePrint.route("/book/add")
def add_book():
    pass


@api_bluePrint.route("/book/delete")
def delete_book():
    pass


@api_bluePrint.route("/book/edit")
def edit_book():
    pass


@api_bluePrint.route("/book/detail/<int:id>")
def detail_book(id):
    if not admin_auth():
        return permissionDenied()

    success = False
    msg = ''
    book = Book.query.get(id)
    if not book:
        msg = 'no such book'
        return jsonify({
            'success': success,
            'msg': msg
        })
    return jsonify({
        'bookInfo': book.to_json()
    })


@api_bluePrint.route("/book/cancel/<int:id>")
def cancel_book(id):
    if not admin_auth():
        return permissionDenied()

    success = False
    msg = ""
    book = Book.query.get(id)
    if not book:
        msg = "no such book"
        return jsonify({
            'success': success,
            'msg': msg,
        })

    if book.status not in [
        BookStatus.NPAID.value,
        BookStatus.PAID.value,
        BookStatus.ACCEPT.value,
        BookStatus.DECLINE.value,
    ]:
        msg = "book status don't support cancel"
        return jsonify({
            'success': success,
            'msg': msg,
        })

    if book.pile:
        if not send_mns_action(book.pile.sn, book.id, 'unbook'):  # send message to queue
            msg += "message send fail. "
    else:
        msg = "book has no pile information"

    book.status = BookStatus.CANCEL.value
    try:
        if book.time_slot:
            db.session.delete(book.time_slot)  # delete time slot
        db.session.add(book)  # change book status
        db.session.commit()
        success = True
    except Exception as e:
        msg += str(e)

    return jsonify({
        'success': success,
        'msg': msg,
    })
