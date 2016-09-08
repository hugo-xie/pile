from ..const import Permission
from flask import request
from ..model.user import User


def get_user():
    token = request.headers.get("token")
    if not token:
        return None
    user = User.verify_auth_token(token)
    return user


def admin_auth():
    user = get_user()
    if user:
        return user.role == Permission.ADMIN
    else:
        return False


def user_auth():
    user = get_user()
    if user:
        return user.role == Permission.USER or user.role == Permission.ADMIN
    else:
        return False


def merchant_auth():
    user = get_user()
    if user:
        return user.role == Permission.MERCHANT or user.role == Permission.ADMIN
    else:
        return False


def maintainer_auth():
    user = get_user()
    if user:
        return user.role == Permission.MAINTAINER or user.role == Permission.ADMIN
    else:
        return False
