import os

DEBUG = False
RELOAD = False
CSRF_ENABLED = True
SECRET_KEY = 'notmysecretkey'
SQLALCHEMY_DATABASE_URI = str(os.environ.get('DATABASE_URL', 'mysql+pymysql://root:root123@localhost/charger?charset=utf8'))

MNS_ACCESS_ID = ''
MNS_ACCESS_KEY = ''
MNS_HOST = ''
