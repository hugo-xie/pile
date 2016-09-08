from flask import jsonify, request, url_for, redirect
from ..const import FLASKY_POSTS_PER_PAGE, permissionDenied
from .role_auth_check import admin_auth
from .. import db
from ..model.terminalParameter import TerminalParameter
from . import api_bluePrint
import json
from datetime import datetime


# terminal_parameter management
@api_bluePrint.route("/terminal_parameter/list", methods=['POST', 'GET'])
def get_terminal_parameters():
    if not admin_auth():
        return permissionDenied()

    page = request.args.get('offset', 1, type=int)
    per_page = request.args.get('limit', FLASKY_POSTS_PER_PAGE, type=int)

    pile_sn = request.args.get('pile_sn', None)
    create_date_start = request.args.get('create_date_start', None)
    create_date_end = request.args.get('create_end', None)
    id = request.args.get('id', None)

    pagination = TerminalParameter.query
    if create_date_start:
        create_date_start = datetime.strptime(create_date_start, '%Y-%m-%d')
        pagination = pagination.filter(TerminalParameter.timestamp >= create_date_start)
    if create_date_end:
        create_date_end = datetime.strptime(create_date_end, '%Y-%m-%d')
        pagination = pagination.filter(TerminalParameter.timestamp >= create_date_end)

    if id:
        pagination = pagination.filter(TerminalParameter.id == id)
    if pile_sn:
        pagination = pagination.filter(TerminalParameter.pile_sn == pile_sn)

    pagination = pagination.order_by(TerminalParameter.version.desc())

    pagination = pagination.paginate(page, per_page=per_page, error_out=False)

    terminal_parameters = pagination.items

    prev = None
    if pagination.has_prev:
        prev = url_for('api.get_terminal_parameters', offset=page - 1, limit=per_page, _external=True)
    next = None
    if pagination.has_next:
        next = url_for('api.get_terminal_parameters', offset=page + 1, limit=per_page, _external=True)
    return jsonify({
        'total': pagination.total,
        'rows': [terminal_parameter.to_json() for terminal_parameter in terminal_parameters],
        'prev': prev,
        'next': next
    })


@api_bluePrint.route("/terminal_parameter/add", methods=['POST'])
def add_terminal_parameter():
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

    terminal_parameter = TerminalParameter()
    for key, value in jsonData.items():
        setattr(terminal_parameter, key, value)

    get_version = None
    if "version" in jsonData:
        get_version = jsonData["version"]

    terminal_parameter.id = None
    terminal_parameter.param = json.dumps(jsonData["param"])
    create_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')  # 当前时间
    terminal_parameter.timestamp = create_time

    terminal_parameter.type = "type"

    if get_version:
        tp = TerminalParameter.query.filter(TerminalParameter.version == get_version).first()
        if tp:  # 如果参数中version在数据库中存在，返回
            msg = "version conflict"
            return jsonify({
                "success": success,
                "msg": msg
            })
        else:
            version = get_version
    else:
        version = generate_version()

    terminal_parameter.version = version

    try:
        db.session.add(terminal_parameter)
        db.session.commit()
        msg = "create terminal_parameter success"
        success = True
    except Exception as e:
        msg = "create terminal_parameter fail." + str(e)

    return jsonify({
        "success": success,
        "msg": msg
        # 'terminal_parameterInfo': terminal_parameter.to_json()
    })


@api_bluePrint.route("/terminal_parameter/delete/<int:id>")
def delete_terminal_parameter(id):
    if not admin_auth():
        return permissionDenied()

    success = False
    msg = ''
    terminal_parameter = TerminalParameter.query.get(id)
    if not terminal_parameter:
        msg = 'no such terminal_parameter'
        return jsonify({
            'success': success,
            'msg': msg
        })
    try:
        db.session.delete(terminal_parameter)
        db.session.commit()
        msg = "delete terminal parameter success. "
        success = True
    except Exception as e:
        msg = "delete fail. " + str(e)
    return jsonify({
        'msg': msg,
        'success': success,
        'terminal_parameterInfo': terminal_parameter.to_json()
    })


@api_bluePrint.route("/terminal_parameter/edit", methods=["POST"])
def edit_terminal_parameter():
    if not admin_auth():
        return permissionDenied()

    success = False
    msg = ''

    jsonData = request.get_json()
    if not jsonData:
        msg = "invalid parameter"
        return jsonify({
            "success": success,
            "msg": msg,
        })
    terminal_id = jsonData["id"]

    terminal_parameter = TerminalParameter.query.get(terminal_id)
    if not terminal_parameter:
        msg = 'no such terminal_parameter'
        return jsonify({
            'success': success,
            'msg': msg
        })

    return redirect(url_for("api.add_terminal_parameter"), code=307)
    # if "param" in jsonData:  # 修改配置参数
    #     terminal_parameter.param = json.dumps(jsonData["param"])
    # if "type" in jsonData:  # 其他字段修改 可选
    #     terminal_parameter.type = jsonData["type"]
    # if "pile_sn" in jsonData:
    #     terminal_parameter.pile_sn = jsonData["pile_sn"]
    # if "status" in jsonData:
    #     terminal_parameter.status = jsonData["status"]
    #
    # version = generate_version()  # 设置版本号
    # terminal_parameter.version = version
    #
    # try:
    #     db.session.add(terminal_parameter)
    #     db.session.commit()
    #     msg = "edit terminal parameter success. "
    #     success = True
    # except Exception as e:
    #     msg = "edit fail. " + str(e)
    # return jsonify({
    #     'msg': msg,
    #     'success': success,
    #     'terminal_parameterInfo': terminal_parameter.to_json()
    # })


@api_bluePrint.route("/terminal_parameter/detail/<int:id>")
def detail_terminal_parameter(id):
    if not admin_auth():
        return permissionDenied()

    success = False
    msg = ''
    terminal_parameter = TerminalParameter.query.get(id)
    if not terminal_parameter:
        msg = 'no such terminal_parameter'
        return jsonify({
            'success': success,
            'msg': msg
        })
    return jsonify({
        'success': success,
        'terminal_parameterInfo': terminal_parameter.to_json()
    })


@api_bluePrint.route("/terminal_parameter/update/<int:id>")  # update待完成
def update(id):
    if not admin_auth():
        return permissionDenied()

    # 补充操作 待完成
    success = False
    msg = ''
    terminal_parameter = TerminalParameter.query.get(id)
    if not terminal_parameter:
        msg = 'no such terminal_parameter'
        return jsonify({
            'success': success,
            'msg': msg
        })
    return jsonify({
        'success': success,
        'terminal_parameterInfo': terminal_parameter.to_json()
    })


@api_bluePrint.route("/terminal_parameter/getVersion")
def version_terminal_parameter():
    if not admin_auth():
        return permissionDenied()

    success = False
    msg = ''

    version = generate_version()
    success = True

    return jsonify({
        'success': success,
        'version': version
    })


def generate_version():
    now = datetime.now()
    day = now.day
    month = now.month
    year = now.year
    if day < 10:
        day = "0" + str(day)
    if month < 10:
        month = "0" + str(month)
    year = str(year)
    dateVersion = year + month + day

    tp = TerminalParameter.query.filter(TerminalParameter.version.like(dateVersion + "%")).order_by(
        TerminalParameter.version.desc()).first()

    if tp:
        numVersion = int(tp.version[8:])
        numVersion += 1
        if numVersion < 10:
            numVersion = "0" + str(numVersion)
        else:
            numVersion = str(numVersion)
    else:
        numVersion = "01"

    version = dateVersion + numVersion

    return version
