from datetime import datetime
from flask import request, redirect, session, abort, jsonify
from flask_admin.contrib.sqla import ModelView
from flask_admin import expose, AdminIndexView, Admin, BaseView
from jinja2 import Markup
from base64 import b64decode
from hashlib import md5
from .. import db, app
from ..model.user import User
from ..model.pile import Pile
from ..model.book import Book
from ..model.pile_app import PileApp
from ..model.report import Report
from ..model.terminal import TerminalImage
from ..const import ADMIN_USER, ADMIN_PASS
from ..model.helper import to_ts
from ..const import ErrNo
from ..route.helper import send_mns_action

def safe_to_int(data, default=None):
    try:
        ans = int(data)
    except ValueError:
        ans = default
    return ans

@app.route('/admin_login', methods=('POST', 'GET'))
def admin_login():
    if 'username' in request.form:
        user = request.form['username']
    else:
        user = None
    if 'password' in request.form:
        password = request.form['password']
    else:
        password = None
    if user == ADMIN_USER and password == ADMIN_PASS:
        session['ts'] = to_ts(datetime.utcnow())
    return redirect('/admin/user/')

@app.route('/admin/param_submit', methods=('POST', ))
def param_submit():
    sn = request.form['pilesn']
    #data = {
    #    'charge': {
    #        'current': safe_to_int(request.form['current']),
    #        'duration': safe_to_int(request.form['duration']),
    #        'watt': safe_to_int(request.form['charge']),
    #    }
    #}
    #app.logger.info('going to send config message: %s to %s', data, sn)
    #send_mns_action(sn, 0, 'config', additional=data)
    operation = request.form.get('operation')
    if operation:
        app.logger.info('going to send config message %s to %s', operation, sn)
        send_mns_action(sn, 0, operation)
    return redirect('/admin/parameterconfigview')

@app.route('/admin/image/upload', methods=('POST', ))
def image_upload():
    if not logged_in():
        abort(403)
    if not request.json:
        abort(400)
    ti = TerminalImage()

    version = request.json.get('version')
    base = request.json.get('base')
    md5sum = request.json.get('md5sum')
    data = request.json.get('base64value')
    if not all((version, base, md5sum, data)):
        return 'missing required param', 400

    ti.base = base
    ti.version = version
    ti.hexfile = data.encode('ascii')
    ti.hexmd5 = md5sum
    md5check = md5(b64decode(ti.hexfile)).hexdigest()

    if md5sum != md5check:
        return 'md5 check failed', 400

    binary = request.json.get('binarybase64value')
    binarymd5sum = request.json.get('binarymd5sum')
    if binary:
        md5check = md5(binary.encode('ascii')).hexdigest()
        if md5check != binarymd5sum:
            return 'binary file md5 check failed', 400
        ti.binfile = binary.encode('ascii')
        ti.binmd5 = md5check

    db.session.add(ti)
    db.session.commit()

    return jsonify(dict(
        ret=ErrNo.OK.value,
        id=ti.id,
    ))

def logged_in():
    return 'ts' in session and to_ts(datetime.utcnow()) - session['ts'] < 1800

class AdminLoginView(AdminIndexView):
    @expose('/')
    def index(self):
        if logged_in():
            return redirect('/admin/user/')
        return self.render('admin/index.html')

    def is_visible(self):
        return not logged_in()

class ViewRequireLogin(ModelView):
    def is_accessible(self):
        return logged_in()

    def inaccessible_callback(self, name):
        return redirect('/admin')

class UploadImageView(BaseView):
    def is_accessible(self):
        return logged_in()

    def inaccessible_callback(self, name):
        return redirect('/admin')

    @expose('/')
    def upload(self):
        return self.render('admin/upload.html')

class ParameterConfigView(BaseView):
    def is_accessible(self):
        return logged_in()

    def inaccessible_callback(self, name):
        return redirect('/admin')

    @expose('/')
    def param_config(self):
        return self.render('admin/config.html')

class UserView(ViewRequireLogin):
    can_view_details = True
    page_size = 50
    column_exclude_list = ['password']
    column_editable_list = ['active']
    column_searchable_list = ['name', 'nick', 'email', 'mobile', 'plate', 'shell']

    def show_license(view, context, model, name):
        if not model.license:
            return ''

        return Markup('<a href="%s" target="_blank"><img src="%s" width="100" height="100"/></a>' %
                      (model.license, model.license))

    def show_avatar(view, context, model, name):
        if not model.avatar:
            return ''

        return Markup('<a href="%s" target="_blank"><img src="%s" width="100" height="100"/></a>' %
                      (model.avatar, model.avatar))

    column_formatters = {
        'license': show_license,
        'avatar': show_avatar
    }


class PileView(ViewRequireLogin):
    can_view_details = True
    page_size = 50
    column_searchable_list = ['sn', 'name', 'address']
    column_filters = ['sn', 'name', 'address']

    def show_user(view, context, model, name):
        if not model.user:
            return ''
        return Markup('<a href="/admin/user/details/?id=%d" target="_blank">%s</a>'%
                      (model.user.id, model.user.name))

    column_formatters = {
        'user': show_user,
    }


class ReportView(ViewRequireLogin):
    can_view_details = True
    page_size = 50
    column_searchable_list = ['comment']
    column_filters = ['comment', 'dt']
    column_editable_list = ['handled']

    def show_evidence(view, context, model, name):
        if not model.evidence:
            return ''

        return Markup('<a href="%s" target="_blank"><img src="%s" width="100" height="100"/></a>' %
                      (model.evidence, model.evidence))

    def show_user(view, context, model, name):
        if not model.user:
            return ''
        return Markup('<a href="/admin/user/details/?id=%d" target="_blank">%s</a>'%
                      (model.user.id, model.user.name))

    column_formatters = {
        'user': show_user,
        'evidence': show_evidence,
    }


class BookView(ViewRequireLogin):
    can_view_details = True
    page_size = 50

    def show_user(view, context, model, name):
        if not model.user:
            return ''
        return Markup('<a href="/admin/user/details/?id=%d" target="_blank">%s</a>'%
                      (model.user.id, model.user.name))

    def show_pile(view, context, model, name):
        if not model.pile:
            return ''
        return Markup('<a href="/admin/pile/details/?id=%d" target="_blank">%s</a>'%
                      (model.pile.id, model.pile.name))

    column_formatters = {
        'user': show_user,
        'pile': show_pile
    }


class PileAppView(ViewRequireLogin):
    can_view_details = True
    page_size = 50

    def show_user(view, context, model, name):
        if not model.user:
            return ''
        return Markup('<a href="/admin/user/details/?id=%d" target="_blank">%s</a>'%
                      (model.user.id, model.user.name))


    column_formatters = {
        'user': show_user,
    }

class ExModelView(ViewRequireLogin):
    can_view_details = True
    page_size = 50

def int2lbytes(i, length=0):
    idx = 0
    while True:
        if not i and (not length or idx >= length):
            break
        yield i & 0xff
        i >>= 8
        idx += 1

def int2bbytes(i, length=0):
    return reversed(tuple(int2lbytes(i, length)))

class TerminalImageView(ViewRequireLogin):
    can_view_details = True
    page_size = 50
    column_exclude_list = ['binfile', 'hexfile']
    column_formatters = {
        "base": lambda v, c, m, p: hex(m.base),
        "version": lambda v, c, m, p: '.'.join('{:x}'.format(s) for s in int2bbytes(m.version, 4)),
    }
    column_labels = {
        "hexmd5": "HEX file MD5",
        "binmd5": "Binary Base64 MD5",
    }


# Create administrative views
admin_intf = Admin(
    app,
    template_mode='bootstrap3',
    base_template='admin/admin_base.html',
    index_view=AdminLoginView(
        name='Admin',
    )
)

admin_intf.add_view(UserView(User, db.session))
admin_intf.add_view(PileView(Pile, db.session))
admin_intf.add_view(ReportView(Report, db.session))
admin_intf.add_view(BookView(Book, db.session))
admin_intf.add_view(PileAppView(PileApp, db.session, name="Pile Application"))
admin_intf.add_view(TerminalImageView(TerminalImage, db.session))
admin_intf.add_view(UploadImageView(name='Upload Terminal Image'))
admin_intf.add_view(ParameterConfigView(name='Pile Parameters'))
