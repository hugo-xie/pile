from . import manager, db
from .const import SettingKey
from .route import helper

@manager.command
def create_db(host, name, password):
    import pymysql
    ms = pymysql.connect(host, name, password)
    cursor = ms.cursor()
    cursor.execute('CREATE DATABASE IF NOT EXISTS charger DEFAULT CHARSET utf8 COLLATE utf8_unicode_ci;')


@manager.command
def prepare_db():
    print("preparing database...")
    db.create_all()


@manager.command
def set_setting(key, value):
    if key in SettingKey.__members__.keys():
        helper.set_setting(SettingKey[key], value)


@manager.command
def get_setting(key):
    if key in SettingKey.__members__.keys():
        return helper.get_setting(SettingKey[key])


if __name__ == "__main__":
    manager.run()
