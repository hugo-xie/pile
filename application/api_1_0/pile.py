from flask import jsonify, request, url_for
from ..const import FLASKY_POSTS_PER_PAGE, permissionDenied
from .role_auth_check import admin_auth, user_auth, maintainer_auth, merchant_auth, get_user
from datetime import datetime
from .. import db
from ..model.pile import Pile
from ..model.pile_app import PileApp
from . import api_bluePrint
from sqlalchemy import or_


# pile management
@api_bluePrint.route("/pile/list", methods=['GET', 'POST'])
def get_piles():
    user = get_user()
    merchant_id = None  # 过滤商家和管理员

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
    # order = request.args.get('asc', 'asc', type=str)
    pile_sn = request.args.get('sn', 0, type=str)  # 电桩ID

    owner_id = request.args.get('owner_id', 0, type=int)  # 商家ID

    longitude_start = request.args.get('longitude_start', 0.0, type=float)
    longitude_end = request.args.get('longitude_end', 0.0, type=float)

    latitude_start = request.args.get('latitude_start', 0.0, type=float)
    latitude_end = request.args.get('latitude_end', 0.0, type=float)

    pagination = Pile.query
    if pile_sn:
        pagination = Pile.query.filter(Pile.sn == pile_sn)

    if longitude_start:
        pagination = pagination.filter(Pile.longitude >= longitude_start)
    if longitude_end:
        pagination = pagination.filter(Pile.longitude < longitude_end)
    if latitude_start:
        pagination = pagination.filter(Pile.longitude >= latitude_start)
    if latitude_end:
        pagination = pagination.filter(Pile.longitude < latitude_end)

    if merchant_id:
        pagination = pagination.filter(Pile.owner_id == merchant_id)

    if owner_id:
        pagination = pagination.filter(Pile.owner_id == owner_id)

    pagination = pagination.filter(or_(Pile.is_deleted == None, Pile.is_deleted == False))  # 过滤已删除电桩
    pagination = pagination.paginate(page, per_page=per_page, error_out=False)

    piles = pagination.items

    prev = None
    if pagination.has_prev:
        prev = url_for('api.get_piles', offset=page - 1, _external=True)
    next = None
    if pagination.has_next:
        next = url_for('api.get_piles', offset=page + 1, _external=True)
    return jsonify({
        'total': pagination.total,
        'rows': [pile.to_json() for pile in piles],
        'prev': prev,
        'next': next
    })


@api_bluePrint.route("/pile/delete/<string:sn>")  # 逻辑删除
def delete_pile(sn):
    if not admin_auth():
        return permissionDenied()

    success = False
    msg = ""

    pile = Pile.query.filter(Pile.sn == sn).first()
    if pile:
        if pile.is_deleted == True:
            msg = "pile already deleted"
        else:
            try:
                pile.is_deleted = True
                db.session.commit()
                msg = "delete pile success"
                success = True
            except:
                msg = "delete pile fail"
    else:
        msg = "no such pile to delete"

    return jsonify({
        "success": success,
        "msg": msg,
        # 'pileInfo': pile.to_json()
    })


@api_bluePrint.route("/pile/edit/<string:sn>", methods=['POST'])
def edit_pile(sn):
    if not admin_auth():
        return permissionDenied()

    success = False
    msg = ""

    pile = Pile.query.filter(Pile.sn == sn).first()

    if not pile:
        msg = "such pile not exist"
        return jsonify({
            "success": success,
            "msg": msg,
        })

    jsonData = request.get_json()
    if not jsonData:
        msg = "invalid parameter"
        return jsonify({
            "success": success,
            "msg": msg,
        })

    for key, value in jsonData.items():
        setattr(pile, key, value)

    try:
        db.session.add(pile)
        db.session.commit()
        msg = "edit pile success"
        success = True
    except Exception as e:
        msg = "edit pile fail" + str(e)

    return jsonify({
        "success": success,
        "msg": msg,
        # 'pileInfo': pile.to_json()
    })


@api_bluePrint.route("/pile/create", methods=['POST'])  # 申请信息删除
def create_pile():
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
    pile_app_id = None
    if "pile_app_id" in jsonData:
        pile_app_id = jsonData["pile_app_id"]
        jsonData.pop("pile_app_id")  # remove pile_app_id
    else:
        msg = "no pile app id"

    create_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')  # 当前时间

    pile = Pile()  # create pile
    pile.create_time = create_time

    for key, value in jsonData.items():
        setattr(pile, key, value)

    try:
        db.session.add(pile)
        db.session.commit()
        msg = "create pile success. "
        success = True
    except Exception as e:
        msg = "create pile fail." + str(e)

    if pile_app_id:
        pile_app = PileApp.query.get(pile_app_id)
        if pile_app:
            if success:  # 如果新建成功，进行删除申请信息
                try:
                    db.session.flush()
                    db.session.delete(pile_app)
                    db.session.commit()
                    msg += " delete pile app success"
                except Exception as e:
                    msg += str(e)
    return jsonify({
        "success": success,
        "msg": msg,
        # 'pileInfo': pile.to_json()
    })


@api_bluePrint.route("/pile/detail/<string:sn>")
def detail_pile(sn):
    success = False
    msg = ''

    user = get_user()
    if not user:
        return permissionDenied()

    pile = Pile.query.filter(Pile.sn == sn).first()
    if not pile:
        msg = 'no such pile or permission denied'
        return jsonify({
            'success': success,
            'msg': msg
        })

    if admin_auth() or user.id == pile.owner_id:
        success = True
        return jsonify({
            'success': success,
            'msg': msg,
            'pileInfo': pile.to_json()
        })
    else:
        return permissionDenied()


@api_bluePrint.route("/pile/edit/work_time", methods=['POST'])
def edit_pile_work_time():
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

    sn = jsonData['sn']
    open_time = jsonData['open_time']
    close_time = jsonData['close_time']

    pile = Pile.query.filter(Pile.sn == sn).first()
    if not pile:
        msg = "such pile not exist"
        return jsonify({
            "success": success,
            "msg": msg,
        })

    pile.open = datetime.strptime(open_time, '%H:%M:%S')
    pile.close = datetime.strptime(close_time, '%H:%M:%S')
    try:
        db.session.add(pile)
        db.session.commit()
        msg = "edit pile working time success"
        success = True
    except Exception as e:
        msg = "edit pile working time fail" + str(e)

    return jsonify({
        "success": success,
        "msg": msg,
        # 'pileInfo': pile.to_json()
    })
