from flask import jsonify, request, url_for
from ..const import FLASKY_POSTS_PER_PAGE, permissionDenied
from .role_auth_check import admin_auth, user_auth, maintainer_auth, merchant_auth
from .. import db
from ..model.pile_app import PileApp
from . import api_bluePrint


@api_bluePrint.route("/pile_app/list")
def get_pill_apps():
    if not admin_auth():
        return permissionDenied()

    page = request.args.get('offset', 1, type=int)
    per_page = request.args.get('limit', FLASKY_POSTS_PER_PAGE, type=int)
    order = request.args.get('asc', 'asc', type=str)

    mobile = request.args.get('mobile', None)
    name = request.args.get('name', '', type=str)

    pagination = PileApp.query
    if mobile:
        pagination = pagination.filter(PileApp.mobile.like("%" + str(mobile) + "%"))
    if name:
        pagination = pagination.filter(PileApp.name.like("%" + str(name) + "%"))

    pagination = pagination.paginate(page, per_page=per_page, error_out=False)

    pileapps = pagination.items

    prev = None
    if pagination.has_prev:
        prev = url_for('api.get_pill_apps', offset=page - 1, _external=True)
    next = None
    if pagination.has_next:
        next = url_for('api.get_pill_apps', offset=page + 1, _external=True)
    return jsonify({
        'total': pagination.total,
        'rows': [pileapp.to_json() for pileapp in pileapps],
        'prev': prev,
        'next': next
    })


@api_bluePrint.route("/pile_app/detail/<int:id>")
def detail_pileapp(id):
    if not admin_auth():
        return permissionDenied()
    success = False
    msg = ''
    pileapp = PileApp.query.get(id)
    if pileapp:
        success = True
    else:
        msg = 'no such pileapp'
        return jsonify({
            'success': success,
            'msg': msg
        })
    return jsonify({
        'success': success,
        'msg': msg,
        'pileappInfo': pileapp.to_json()
    })
