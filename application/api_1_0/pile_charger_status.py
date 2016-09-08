from flask import jsonify
from ..model.terminal import TerminalChargeStatus
from ..const import FLASKY_POSTS_PER_PAGE, permissionDenied
from .role_auth_check import admin_auth, user_auth, maintainer_auth, merchant_auth, get_user
from . import api_bluePrint


@api_bluePrint.route("/pile_charge_status/detail/<int:sn>")
def detail_pile_charge_status(sn):
    if not admin_auth():
        return permissionDenied()

    success = False
    msg = ''
    pile_charge_status = TerminalChargeStatus.query.filter(TerminalChargeStatus.sn == sn).first()
    if not pile_charge_status:
        msg = 'no such pile stauts'
        return jsonify({
            'success': success,
            'msg': msg
        })
    return jsonify({
        'success': success,
        'msg': msg,
        'pile_charge_statusInfo': pile_charge_status.to_json()
    })
