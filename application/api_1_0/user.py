from flask import jsonify, request, url_for
from ..const import FLASKY_POSTS_PER_PAGE, permissionDenied, Permission
from .role_auth_check import admin_auth, user_auth, maintainer_auth, merchant_auth

from .. import db
from ..model.user import User
from . import api_bluePrint


# 用户登陆,类型判别,授权
@api_bluePrint.route("/login", methods=['POST', 'GET'])
def login():
    success = False
    msg = "test"
    # token = request.headers.get("token")
    username = request.get_json()["username"]
    password = str(request.get_json()["password"])

    user = User.query.filter(User.name == username).first()
    token = None
    if user:
        if user.verify(password):
            id = user.id
            if user.can_login:
                success = True
                token = User.generate_auth_token(id=id)
            else:
                msg = "permission denied"
        else:
            msg = "invalid password"
    else:
        msg = "invalid username"
        return jsonify({
            'success': success,
            'msg': msg,
        })

    return jsonify({
        'success': success,
        'token': token,
        'user': user.to_json()
    })


# user management
@api_bluePrint.route("/user/list", methods=['POST', 'GET'])
def get_users():
    if not admin_auth():
        return permissionDenied()

    page = request.args.get('offset', 1, type=int)
    per_page = request.args.get('limit', FLASKY_POSTS_PER_PAGE, type=int)
    order = request.args.get('asc', 'asc', type=bool)
    mobile = request.args.get('mobile', None)
    plate = request.args.get('plate', None)
    onlyOwner = request.args.get('onlyOwner', "", type=str) # change to support to check the pile owner

    pagination = User.query
    if mobile:
        pagination = pagination.filter(User.mobile.like("%" + str(mobile) + "%"))
    if plate:
        pagination = pagination.filter(User.plate.like("%" + str(plate) + "%"))

    if onlyOwner == "true":
        pagination = pagination.filter(User.piles != None)

    pagination = pagination.paginate(page, per_page=per_page, error_out=False)

    users = pagination.items

    prev = None
    if pagination.has_prev:
        prev = url_for('api.get_users', offset=page - 1, limit=per_page, _external=True)
    next = None
    if pagination.has_next:
        next = url_for('api.get_users', offset=page + 1, limit=per_page, _external=True)
    return jsonify({
        'total': pagination.total,
        'rows': [user.to_json() for user in users],
        # 'piles': [pile.to_json() for user in users for pile in user.piles],
        'prev': prev,
        'next': next
    })


@api_bluePrint.route("/user/add", methods=['POST'])
def add_user():
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

    user = User()
    for key, value in jsonData.items():
        setattr(user, key, value)

    try:
        db.session.add(user)
        db.session.commit()
        msg = "create user success"
        success = True
    except Exception as e:
        msg = "create user fail." + str(e)

    return jsonify({
        "success": success,
        "msg": msg,
        'userInfo': user.to_json()
    })


@api_bluePrint.route("/user/delete")
def delete_user():
    pass


@api_bluePrint.route("/user/edit")
def edit_user():
    pass


@api_bluePrint.route("/user/detail/<int:id>")
def detail_user(id):
    if not admin_auth():
        return permissionDenied()

    success = False
    msg = ''
    user = User.query.get(id)
    if not user:
        msg = 'no such user'
        return jsonify({
            'success': success,
            'msg': msg
        })
    return jsonify({
        'userInfo': user.to_json()
    })


@api_bluePrint.route("/user/allow_login/<int:id>")
def allow_user_login(id):
    if not admin_auth():
        return permissionDenied()
    success = False
    msg = ""
    user = User.query.get(id)
    if not user:
        msg = "no such user"
        return jsonify({
            'success': success,
            'msg': msg,
        })
    if user.can_login:
        msg = "already can login in the system"
    else:
        user.can_login = True
        user.role = Permission.MERCHANT
        db.session.add(user)
        db.session.commit()
        success = True
        msg = "allow the user to login in"

    return jsonify({
        'success': success,
        'msg': msg,
        'userInfo': user.to_json()
    })


@api_bluePrint.route("/user/deny_login/<int:id>")
def deny_user_login(id):
    if not admin_auth():
        return permissionDenied()
    success = False
    msg = ""
    user = User.query.get(id)
    if not user:
        msg = "no such user"
        return jsonify({
            'success': success,
            'msg': msg,
        })
    if not user.can_login:
        msg = "still can not login in the system"
    else:
        user.can_login = False
        user.role = Permission.USER
        db.session.add(user)
        db.session.commit()
        success = True
        msg = "deny the user to login in"

    return jsonify({
        'success': success,
        'msg': msg,
        'userInfo': user.to_json()
    })
