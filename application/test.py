import simplejson
import urllib
import httplib2
from . import manager, db
from .route import helper
from .const import SettingKey, ErrNo


host = 'http://127.0.0.1:5000'
username = 'wei'
password = 'wei123'


@manager.command
def del_db():
    db.session.execute('drop database if exists charger;')


@manager.command
def start_mysql():
    import os
    os.system('net start mysql57')


@manager.command
def init_db(host, name, password):
    import pymysql
    ms = pymysql.connect(host, name, password)
    cursor = ms.cursor()
    cursor.execute('CREATE DATABASE IF NOT EXISTS charger DEFAULT CHARSET utf8 COLLATE utf8_unicode_ci;')

    db.create_all()

    helper.set_setting(SettingKey.SMS_ACCOUNT, '422134981')
    helper.set_setting(SettingKey.SMS_PASSWORD, '0AFA41128360DBB72907E5F0C6D8')
    helper.set_setting(SettingKey.VERSION, '1.00')

    reg_user('wei', 'wei123', '13564374378', '1234', 'ww', '0000', '1111', 'w@w.com', r'c:\numbers\1.jpg')
    reg_user('admin', 'admin123', '13564374379', '1234', 'amin', '0001', '1112', 'admin@w.com', r'c:\numbers\1.jpg')
    add_friend('admin', 'admin123', '13564374378')
    process_friend_req(1, 1)

    for i in range(1, 10):
        sn = 'SN' + str(i)
        name = 'PILE' + str(i)
        address = 'ADDRESS' + str(i)
        import random
        long = round(random.random() * 100, 13)
        lat = round(random.random() * 100, 13)
        auto_check = random.randint(0,1)
        electricity = random.randint(10, 100)
        service = random.randint(10, 100)
        appointment = random.randint(10, 100)
        open = '8:00:00'
        close = '18:00:00'
        if auto_check == 1:
            auto_check_start = '"2016-3-10 8:00:00"'
            auto_check_end = '"2016-3-18 18:00:00"'
        else:
            auto_check_start = 'NULL'
            auto_check_end = 'NULL'
        owner_id = 1
        support = 0
        cmd = 'insert into pile values(NULL, "%s", "%s", %f, %f, "%s", %d, %d, %d, %d, "%s", "%s", %s, %s, ' \
              'NULL, NULL, %d, %d, NULL, NULL)' % (sn, name, long, lat, address, auto_check, electricity, service, appointment, open, close,
                                   auto_check_start, auto_check_end, owner_id, support)
        db.session.execute(cmd)
        db.session.commit()


def encode_file(path):
    import base64
    f = open(path,'rb')
    result = base64.encodebytes(f.read())
    f.close()
    return result


@manager.command
def b64en(path):
    import base64
    f = open(path,'rb')
    result = base64.encodebytes(f.read())
    f.close()


def get(url):
    h = httplib2.Http()
    try:
        (resp_headers, content) = h.request(url, 'GET')
        msg = content.decode()
        print(msg)
        return True, msg
    except httplib2.HttpLib2Error as e:
        return False, str(e)


def post(url, headers, data):
    h = httplib2.Http()
    try:
        (resp_headers, content) = h.request(url, 'POST', headers=headers, body=data)
        msg = content.decode()
        print(msg)
        json = simplejson.loads(msg)
        if json['ret'] != 0:
            print(str(ErrNo(json['ret'])))
        return True, msg
    except simplejson.JSONDecodeError as e:
        print(str(e))
        return False, str(e)
    except httplib2.HttpLib2Error as e:
        print(str(e))
        return False, str(e)


def post_json(url, params):
    headers = {'Content-type': 'application/json; charset=UTF-8'}
    data = bytes(simplejson.dumps(params), encoding='utf8')
    return post(host + url, headers, data)


def post_form(url, params):
    data = urllib.parse.urlencode(params)
    headers = {'Content-type': 'application/x-www-form-urlencoded; charset=UTF-8'}
    return post(host + url, headers, data)


@manager.command
def reg_user(name, password, mobile, code, nick, plate, shell, email, license):
    params = locals()
    import base64
    f=open(license,'rb')
    content = base64.encodebytes(f.read())
    f.close()
    params['license'] = content
    post_json('/v1/user/register', params)


@manager.command
def update_user(name, password, nick, email, avatar):
    ret, token = get_token(name, password)
    if not ret:
        return
    import base64
    f=open(avatar,'rb')
    content = base64.encodebytes(f.read())
    f.close()
    json = {'token': token,
            'nick': nick,
            'email': email,
            'avatar': content}
    url = '/v1/user/update'
    post_json(url, json)


@manager.command
def login(name, password):
    json = {'name': name,
            'password': password}
    return post_json('/v1/user/login', json)


@manager.command
def get_token(name, password):
    ret, msg = login(name, password)
    if not ret:
        return ret, msg
    json = simplejson.loads(msg)
    if json['ret'] != 0:
        return False, None
    token = json['token']
    return True, token


@manager.command
def logout(name, password):
    ret, token = get_token(name, password)
    if not ret:
        return
    json = {'token': token}
    url = '/v1/user/logout'
    post_json(url, json)


@manager.command
def get_user(name, password):
    ret, token = get_token(name, password)
    if ret:
        json = {'token': token}
        url = '/v1/user/info'
        post_json(url, json)


@manager.command
def search_pile(llong, rlong, ulat, blat):
    params = locals()
    url = '/v1/piles/search'
    post_json(url, params)


@manager.command
def get_pile(id):
    params = locals()
    url = '/v1/piles/info'
    post_json(url, params)


@manager.command
def book_pile(name, password, pile_id, start, end):
    params = locals()
    ret, token = get_token(name, password)
    if not ret:
        return
    from datetime import datetime
    start = datetime.strptime(start, "%Y-%m-%d %H:%M:%S")
    end = datetime.strptime(end, "%Y-%m-%d %H:%M:%S")
    from .model.helper import to_ts
    del(params['name'])
    del(params['password'])
    params['start'] = to_ts(start)
    params['end'] = to_ts(end)
    params['token'] = token
    url = '/v1/books/new'
    post_json(url, params)


@manager.command
def pay(name, password, id, money):
    params = locals()
    del(params['name'])
    del(params['password'])
    ret, token = get_token(name, password)
    if not ret:
        return
    params['token'] = token
    url = '/v1/payment/pay'
    post_json(url, params)


@manager.command
def book_history(name, password, type):
    params = locals()
    del(params['name'])
    del(params['password'])
    ret, token = get_token(name, password)
    if not ret:
        return
    params['token'] = token
    url = '/v1/books/all'
    post_json(url, params)


@manager.command
def book_action(name, password, id, action):
    params = locals()
    del(params['name'])
    del(params['password'])
    ret, token = get_token(name, password)
    if not ret:
        return
    params['token'] = token
    url = '/v1/books/action'
    post_json(url, params)


@manager.command
def sms_code(mobile):
    params = locals()
    url = '/v1/user/code'
    post_json(url, params)


@manager.command
def book_info(name, password, id):
    params = locals()
    del(params['name'])
    del(params['password'])
    ret, token = get_token(name, password)
    if not ret:
        return
    params['token'] = token
    url = '/v1/books/info'
    post_json(url, params)


@manager.command
def pile_books(name, password, id):
    params = locals()
    del(params['name'])
    del(params['password'])
    ret, token = get_token(name, password)
    if not ret:
        return
    params['token'] = token
    url = '/v1/books/pile'
    post_json(url, params)


def func_with_login(params, url):
    if 'name' in params:
        name = params['name']
        del params['name']
    else:
        name = username
    if 'password' in params:
        passwd = params['password']
        del params['password']
    else:
        passwd = password
    ret, token = get_token(name, passwd)
    if not ret:
        return
    params['token'] = token
    post_json(url, params)


def func_without_login_info(params, url):
    ret, token = get_token(username, password)
    if not ret:
        return
    params['token'] = token
    post_json(url, params)


@manager.command
def list_piles(name, password):
    func_with_login(locals(), '/v1/piles/list')


@manager.command
def update_pile(id, name, service, electricity, appointment, open, close, auto_ack, auto_ack_start, auto_ack_end):
    func_without_login_info(locals(), '/v1/piles/update')


@manager.command
def list_reqs():
    func_with_login(locals(), '/v1/books/requests')


@manager.command
def apply_build_pile(choice, name, ident, mobile, comment):
    func_without_login_info(locals(), '/v1/requests/apply')


@manager.command
def reset_password(mobile):
    post_json('/v1/user/reset_password', locals())


@manager.command
def add_friend(name, password, mobile):
    func_with_login(locals(), '/v1/friends/add')


@manager.command
def list_friend_reqs():
    func_with_login(locals(), '/v1/friends/list_req')


@manager.command
def process_friend_req(id, accept):
    func_with_login(locals(), '/v1/friends/process_req')


@manager.command
def list_friend():
    func_with_login(locals(), '/v1/friends/list')


@manager.command
def get_friend(id):
    func_with_login(locals(), '/v1/friends/get')


@manager.command
def del_friend(id):
    func_with_login(locals(), '/v1/friends/del')


@manager.command
def topup(name, password, money, account):
    func_with_login(locals(), '/v1/wallet/topup')


@manager.command
def withdraw(money, account):
    func_with_login(locals(), '/v1/wallet/withdraw')


@manager.command
def trans():
    func_with_login(locals(), '/v1/wallet/transactions')


@manager.command
def version():
    post_json('/v1/system/version', None)


@manager.command
def messages():
    post_json('/v1/system/messages', None)


@manager.command
def report(comment, evidence):
    evidence = encode_file(evidence)
    func_with_login(locals(), '/v1/system/report')


@manager.command
def update_passwd(name, password, code, new_passwd):
    ret, token = get_token(name, password)
    if not ret:
        return
    params = {}
    params['token'] = token
    params['code'] = code
    params['password'] = new_passwd
    url = '/v1/user/update_password'
    post_json(url, params)


@manager.command
def update_friend(id, nick, appointment, electricity, service):
    func_with_login(locals(), '/v1/friends/update')


@manager.command
def share():
    func_with_login(locals(), '/v1/system/share')


@manager.command
def process_book(id, accept):
    func_with_login(locals(), '/v1/books/process')


@manager.command
def show_stat(name, password):
    func_with_login(locals(), '/v1/user/statistics')


@manager.command
def show_rank(name, password):
    func_with_login(locals(), '/v1/user/rank')


def mk_get_url(url, params):
    full_url = '%s%s?' % (host, url)
    for k, v in params.items():
        full_url = '%s%s=%s&' % (full_url, k, v)
    full_url = full_url[:-1]
    print(full_url)
    return full_url


@manager.command
def reg_term(mobile, pid):
    print(locals().items())
    url = mk_get_url('/v1/terminal/reg', locals())
    get(url)


@manager.command
def new_term_info(mobile, pid, stat_gun,stat_lock, stat_charge, stat_run, info_charged, info_current, info_volt,
                  info_int_temp, info_plug_temp, info_env_temp, info_pm25):
    url = mk_get_url('/v1/terminal/info/new', locals())
    get(url)



