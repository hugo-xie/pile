from flask import jsonify, request
from ..model.statistic import Statistic
from . import api_bluePrint


# book management
@api_bluePrint.route("/assess/pile")  # check the pile statistic, waiting to complete
def pile_assess():
    pile_id = request.args.get('id', None, type=int)
    month_start = request.args.get('month_start', None, type=str)
    month_end = request.args.get('month_start', None, type=str)

    return jsonify({
        'success': False,
        'rows': [{
            'earning': 1900,
            'pile_id': 1,
            'use_rate': 0.511,
            'charge_amount': 2001,
            'month': "2016-05"}, {
            'earning': 1900,
            'id': 1,
            'use_rate': 0.511,
            'charge_amount': 2001,
            'month': "2016-06"}]
    })


@api_bluePrint.route("/assess/user/<int:id>")
def user_assess(id):
    success = False
    msg = ''
    userStatistic = Statistic.query.filter(Statistic.user_id == id).first()
    if not userStatistic:
        msg = 'no such user statistic'
        return jsonify({
            'success': success,
            'msg': msg
        })
    return jsonify({
        'success': True,
        'msg': msg,
        'userStatistic': userStatistic.to_json()
    })


@api_bluePrint.route("/assess/platform")
def assess_platform():
    success = False
    msg = ''
    return jsonify({
        'success': False,
        'msg': msg,
        'rows': [{
            'market': 0.5,
            'electricity_amount': 200000,
            'service_amount': 2000,
            'use_rate': 0.771,
            'fault_rate': 0.023,
            'report_rate': 0.001,
            'month': "2016-05"}, {
            'market': 0.5,
            'electricity_amount': 200000,
            'service_amount': 2000,
            'use_rate': 0.771,
            'fault_rate': 0.023,
            'repor_rate': 0.001,
            'month': "2016-05"
        }]
    })


@api_bluePrint.route("/assess/report")
def assess_report():
    return jsonify({
        'message': False,
        'content': "this is the report content"
    })
