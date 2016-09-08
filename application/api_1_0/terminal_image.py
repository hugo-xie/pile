from flask import jsonify, request, url_for
from ..model.terminal import TerminalImage
from ..const import FLASKY_POSTS_PER_PAGE, permissionDenied
from .role_auth_check import admin_auth, user_auth, maintainer_auth, merchant_auth
from . import api_bluePrint
from hashlib import md5
from base64 import b64decode
from .. import db


@api_bluePrint.route("/terminal_image/list")
def get_terminal_images():
    if not admin_auth():
        return permissionDenied()

    page = request.args.get('offset', 1, type=int)
    per_page = request.args.get('limit', FLASKY_POSTS_PER_PAGE, type=int)
    order = request.args.get('asc', 'asc', type=str)
    # terminal_image_start = request.args.get('terminal_image_start', "", type=str)
    # terminal_image_end = request.args.get('terminal_image_end', "", type=str)
    #
    # id = request.args.get('id', None, type=int)
    # user_id = request.args.get('user_id', None, type=int)
    #
    pagination = TerminalImage.query
    # if terminal_image_start:
    # 	terminal_image_start = datetime.strptime(terminal_image_start, '%Y-%m-%d %H:%M:%S')
    # 	pagination = pagination.filter(TerminalImage.terminal_image_start >= terminal_image_start)
    # if terminal_image_end:
    # 	terminal_image_end = datetime.strptime(terminal_image_end, '%Y-%m-%d %H:%M:%S')
    # 	pagination = pagination.filter(TerminalImage.terminal_image_start < terminal_image_end)
    # if id:
    # 	pagination = pagination.filter(TerminalImage.id == id)
    # if user_id:
    # 	pagination = pagination.filter(TerminalImage.user_id == user_id)
    pagination = pagination.paginate(page, per_page=per_page, error_out=False)

    terminal_images = pagination.items

    prev = None
    if pagination.has_prev:
        prev = url_for('api.get_terminal_images', offset=page - 1, _external=True)
    next = None
    if pagination.has_next:
        next = url_for('api.get_terminal_images', offset=page + 1, _external=True)
    return jsonify({
        'total': pagination.total,
        'rows': [terminal_image.to_json() for terminal_image in terminal_images],
        'prev': prev,
        'next': next
    })


@api_bluePrint.route("/terminal_image/detail/<int:id>")
def detail_terminal_image(id):
    if not admin_auth():
        return permissionDenied()

    success = False
    msg = ''
    terminal_image = TerminalImage.query.get(id)
    if not terminal_image:
        msg = 'no such terminal_image'
        return jsonify({
            'success': success,
            'msg': msg
        })
    else:
        success = True
    return jsonify({
        'success': success,
        'msg': msg,
        'info': terminal_image.to_json()
    })


@api_bluePrint.route("/terminal_image/add", methods=["POST"])
def add_terminal_image():
    if not admin_auth():
        return permissionDenied()
    success = False
    msg = ''

    jsonData = request.json

    if not jsonData:
        msg = "no parameter"
        return jsonify({
            "success": success,
            "msg": msg
        })
    version = jsonData.get('version')
    base = jsonData.get('base')
    md5sum = jsonData.get('md5sum')
    data = jsonData.get('base64value')
    binary = jsonData.get('binarybase64value')
    binarymd5sum = jsonData.get('binarymd5sum')

    ti = TerminalImage()
    ti.base = base
    ti.version = version
    ti.hexfile = data.encode('ascii')
    ti.hexmd5 = md5sum
    md5check = md5(b64decode(ti.hexfile)).hexdigest()

    if md5sum != md5check:
        msg = 'md5 check failed'
        return jsonify({
            "success": success,
            "msg": msg
        })

    if binary:
        md5check = md5(binary.encode('ascii')).hexdigest()
        if md5check != binarymd5sum:
            msg = 'binary file md5 check failed'
            return jsonify({
                "success": success,
                "msg": msg
            })
        ti.binfile = binary.encode('ascii')
        ti.binmd5 = md5check

    try:
        db.session.add(ti)
        db.session.commit()
        success = True
    except Exception as e:
        msg = "upload fail" + str(e)

    return jsonify({
        'success': success,
        'msg': msg,
        # 'Info': ti.to_json()
    })


@api_bluePrint.route("/terminal_image/delete/<int:id>")
def delete_terminal_image(id):
    if not admin_auth():
        return permissionDenied()

    success = False
    msg = ""

    terminal_image = TerminalImage.query.get(id)
    if terminal_image:
        try:
            db.session.delete(terminal_image)
            db.session.commit()
            success = True
            msg = "delete success"
        except Exception as e:
            msg = "delete terminal image fail" + str(e)
    else:
        msg = "no such terminal image"
    return jsonify({
        "success": success,
        "msg": msg,
        # 'Info': terminal_image.to_json()
    })


@api_bluePrint.route("/terminal_image/edit")
def edit_terminal_image():
    pass


@api_bluePrint.route("/terminal_image/upgrade/single/<int:id>")
def terminal_image_upgrade_single(id):
    pass


@api_bluePrint.route("/terminal_image/upgrade/all")
def terminal_image_upgrade_all():
    pass
