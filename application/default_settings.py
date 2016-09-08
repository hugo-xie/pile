import os

# Get application base dir.
_basedir = os.path.abspath(os.path.dirname(__file__))

DEBUG = True
RELOAD = True
SECRET_KEY = 'mysecretkeyvalue'

SQLALCHEMY_DATABASE_URI = 'mysql+pymysql://root:root@localhost:3307/charger?charset=utf8'
# SQLALCHEMY_DATABASE_URI = 'mysql+pymysql://root:admin@localhost:3306/charger?charset=utf8'
SQLALCHEMY_TRACK_MODIFICATIONS = True
