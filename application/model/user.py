from hashlib import md5
from .wallet import Wallet
from .statistic import Statistic
from .. import db
from itsdangerous import SignatureExpired, BadSignature, TimedJSONWebSignatureSerializer as Serializer
from ..default_settings import SECRET_KEY
from ..const import TOKEN_TIME_OUT_MIN


class User(db.Model):
    """
    This class define user structure.

    id : record id
    name : user name
    nick : user nickname
    email : email address
    password : password (md5 value)
    mobile : user mobile phone number
    plate : plate
    shell : shell
    license : license picture (file storage object id)
    avatar : avatar picture (file storage object id)
    active : whether the account is active
    piles : piles the user owns
    books : books the user applies
    pile_apps : user's application for new user
    friend_apps : user's application for new friend
    friends : user's friends
    wallet : user's wallet object
    reports : user's reports list
    statistic : user's statistic information
    points : user's points
    """
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), unique=True)
    nick = db.Column(db.String(80), unique=True)
    email = db.Column(db.String(80), unique=True)
    password = db.Column(db.String(80))
    mobile = db.Column(db.String(80), unique=True)
    plate = db.Column(db.String(80))
    shell = db.Column(db.String(80))
    license = db.Column(db.String(80))
    avatar = db.Column(db.String(80))
    active = db.Column(db.Boolean)
    # add new columns
    role = db.Column(db.String(80))
    can_login = db.Column(db.Boolean)
    account_credits = db.Column(db.Integer, default=0)

    piles = db.relationship('Pile', backref='user', lazy='dynamic')
    books = db.relationship('Book', backref='user', lazy='dynamic')

    pile_apps = db.relationship('PileApp', backref='user', lazy='dynamic')
    friend_apps = db.relationship('FriendApp', backref='user', primaryjoin='FriendApp.target_id==User.id',
                                  lazy='dynamic')
    friends = db.relationship('Friend', backref='user', primaryjoin='Friend.user_id==User.id', lazy='dynamic')
    wallet = db.relationship('Wallet', backref='user', uselist=False)
    reports = db.relationship('Report', backref='user', lazy='dynamic')
    statistic = db.relationship('Statistic', backref='user', uselist=False)
    points = db.relationship('Point', backref='user', lazy='dynamic')

    def __init__(self, name=None, nick=None, email=None, password="1111", mobile=None, plate=None, shell=None, license=None, avatar=None):
        self.name = name
        self.nick = nick
        self.email = email
        self.password = md5(password.encode('utf-8')).hexdigest()  # save md5 of password to database
        self.mobile = mobile
        self.plate = plate
        self.shell = shell
        self.license = license
        self.avatar = avatar
        self.active = True

    # this method will be called when new User is created, commit will be called by caller
    def prepare_user(self):
        if self.statistic is None:
            statistic = Statistic(self.id)
            db.session.add(statistic)
        if self.wallet is None:
            wallet = Wallet(self.id)
            db.session.add(wallet)

    def verify(self, password):
        if md5(password.encode('utf-8')).hexdigest() == self.password:
            return True
        return False

    @staticmethod
    def password_md5(password):
        return md5(password.encode('utf-8')).hexdigest()

    def to_json(self):
        if self.nick is None or self.nick == '':
            self.nick = "Guest" + str(self.id)
        attrs = (
            'id', 'name', 'nick', 'email', 'mobile', 'plate', 'shell', 'license', 'avatar', 'role', 'can_login',
            'password', 'account_credits')
        ans = {attr: self.__getattribute__(attr) for attr in attrs}
        if self.wallet:
            ans['available'] = self.wallet.available
            ans['balance'] = self.wallet.balance
        return ans

    @staticmethod
    def generate_auth_token(id=None, expiration=TOKEN_TIME_OUT_MIN):  # half an hour to be invalid
        s = Serializer(SECRET_KEY, expires_in=expiration)
        return s.dumps({'id': id})

    @staticmethod
    def verify_auth_token(token):
        s = Serializer(SECRET_KEY)
        try:
            data = s.loads(token)
        except SignatureExpired:
            return None  # valid token, but expired
        except BadSignature:
            return None  # invalid token
        user = User.query.get(data['id'])
        return user
