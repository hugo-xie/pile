from flask import jsonify, request, url_for
from ..model.report import Report
from ..model.user import User
from ..const import FLASKY_POSTS_PER_PAGE, permissionDenied
from .role_auth_check import admin_auth, user_auth, maintainer_auth, merchant_auth
from . import api_bluePrint
from .. import db
from datetime import datetime


@api_bluePrint.route("/report/list")
def get_reports():
    if not admin_auth():
        return permissionDenied()

    page = request.args.get('offset', 1, type=int)
    per_page = request.args.get('limit', FLASKY_POSTS_PER_PAGE, type=int)
    order = request.args.get('asc', 'asc', type=str)
    report_start = request.args.get('report_start', "", type=str)
    report_end = request.args.get('report_end', "", type=str)

    id = request.args.get('id', None, type=int)
    user_id = request.args.get('user_id', None, type=int)

    pagination = Report.query
    if report_start:
        report_start = datetime.strptime(report_start, '%Y-%m-%d %H:%M:%S')
        pagination = pagination.filter(Report.dt >= report_start)
    if report_end:
        report_end = datetime.strptime(report_end, '%Y-%m-%d %H:%M:%S')
        pagination = pagination.filter(Report.dt <= report_end)
    if id:
        pagination = pagination.filter(Report.id == id)
    if user_id:
        pagination = pagination.filter(Report.user_id == user_id)
    pagination = pagination.paginate(page, per_page=per_page, error_out=False)

    reports = pagination.items

    prev = None
    if pagination.has_prev:
        prev = url_for('api.get_reports', offset=page - 1, _external=True)
    next = None
    if pagination.has_next:
        next = url_for('api.get_reports', offset=page + 1, _external=True)
    return jsonify({
        'total': pagination.total,
        'rows': [report.to_json() for report in reports],
        'prev': prev,
        'next': next
    })


@api_bluePrint.route("/report/handled", methods=['GET', 'POST'])
def handle_report():
    if not admin_auth():
        return permissionDenied()

    success = False
    msg = ""

    jsonData = request.get_json()
    if not jsonData:
        msg = "invalid parameter"
        return jsonify({
            "success": success,
            "msg": msg,
        })

    plate = None
    deduct_score = None
    bonus_score = None
    comment = None
    report_id = None
    report_user_id = None
    if "report_id" in jsonData:
        report_id = jsonData["report_id"]
    if "report_user_id" in jsonData:
        report_user_id = jsonData["report_user_id"]
    if "plate" in jsonData:
        plate = jsonData["plate"]
    if "deduct_score" in jsonData:
        deduct_score = jsonData["deduct_score"]
    if "bonus_score" in jsonData:
        bonus_score = jsonData["bonus_score"]
    if "comment" in jsonData:
        comment = jsonData["comment"]

    report = Report.query.get(report_id)

    reported_user = User.query.filter(User.plate == plate).first()
    report_user = User.query.get(report_user_id)

    if report and report_user and reported_user:
        report.comment = comment
        if not report.handled:
            report.handled = True
        else:
            msg = 'report already be handled'
            return jsonify({
                "success": success,
                "msg": msg
            })
        if report_user.account_credits:
            report_user.account_credits += int(bonus_score)
        else:
            report_user.account_credits = int(bonus_score)

        if reported_user.account_credits:
            reported_user.account_credits -= int(deduct_score)
        else:
            reported_user.account_credits = -int(deduct_score)

        try:
            db.session.add(report)
            db.session.add(reported_user)
            db.session.add(report_user)
            db.session.commit()
            msg = "handled report success"
            success = True
        except Exception as e:
            msg = "edit report fail." + str(e)
    else:
        msg = 'no such report'
        return jsonify({
            "success": success,
            "msg": msg
        })

    return jsonify({
        "success": success,
        "msg": msg,
        'pileInfo': report.to_json()
    })


@api_bluePrint.route("/report/add_credits", methods=['GET', 'POST'])
def add_credits():
    if not admin_auth():
        return permissionDenied()

    success = False
    msg = ""

    report_id = request.form.get('id', None, type=int)
    handled = request.form.get('handled', None, type=bool)
    comment = request.form.get('comment', None, type=str)

    report = Report.query.get(report_id)

    if report:
        report.comment = comment
        report.handled = handled
        try:
            # db.session.add(report)
            # db.session.commit()
            msg = "handled report success"
            success = True
        except:
            msg = "edit report fail"
    else:
        msg = 'no such report or cannot find reporter'
        return jsonify({
            "success": success,
            "msg": msg
        })

    return jsonify({
        "success": success,
        "msg": msg,
        'pileInfo': report.to_json()
    })


@api_bluePrint.route("/report/delete_credits", methods=['GET', 'POST'])
def delete_credits():
    if not admin_auth():
        return permissionDenied()

    success = False
    msg = ""

    report_id = request.form.get('id', None, type=int)
    handled = request.form.get('handled', None, type=bool)
    comment = request.form.get('comment', None, type=str)

    report = Report.query.get(report_id)

    if report:
        report.comment = comment
        report.handled = handled
        try:
            # db.session.add(report)
            # db.session.commit()
            msg = "handled report success"
            success = True
        except:
            msg = "edit report fail"
    else:
        msg = 'no such report'
        return jsonify({
            "success": success,
            "msg": msg
        })

    return jsonify({
        "success": success,
        "msg": msg,
        'pileInfo': report.to_json()
    })


@api_bluePrint.route("/report/detail/<int:id>")
def detail_report(id):
    if not admin_auth():
        return permissionDenied()

    success = False
    msg = ''
    report = Report.query.get(id)
    if not report:
        msg = 'no such report'
        return jsonify({
            'success': success,
            'msg': msg
        })
    else:
        success = True
    return jsonify({
        'success': success,
        'msg': msg,
        'bookInfo': report.to_json()
    })


@api_bluePrint.route("/report/add")
def add_report():
    pass


@api_bluePrint.route("/report/delete")
def delete_report():
    pass


@api_bluePrint.route("/report/edit")
def edit_report():
    pass
