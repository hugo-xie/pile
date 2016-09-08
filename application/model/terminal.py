from datetime import datetime
from ..model.helper import to_ts
from .. import db


class Terminal(db.Model):
    """
    This class defines terminal information structure.

    id : record id
    sn : serial number
    mobile : pile mobile number
    ts : timestamp
    status : data
    """
    id = db.Column(db.Integer, primary_key=True)
    sn = db.Column(db.String(80), db.ForeignKey('pile.sn'))
    mobile = db.Column(db.String(16), nullable=False)
    ts = db.Column(db.DateTime)
    status = db.Column(db.SmallInteger)

    def __init__(self, mobile, sn, status, ts=None):
        self.mobile = mobile
        self.sn = sn
        self.status = status
        self.ts = ts if ts else datetime.utcnow()


class TerminalInfo(db.Model):
    id = db.Column(db.BigInteger, primary_key=True)
    sn = db.Column(db.String(80), db.ForeignKey('pile.sn'))
    mobile = db.Column(db.String(16))
    stat_gun = db.Column(db.SmallInteger)
    stat_lock = db.Column(db.SmallInteger)
    stat_charge = db.Column(db.SmallInteger)
    stat_run = db.Column(db.SmallInteger)
    stat_net = db.Column(db.SmallInteger)
    stat_battery = db.Column(db.SmallInteger)
    stat_work = db.Column(db.SmallInteger)
    info_temp1 = db.Column(db.DECIMAL(5, 1))  # 2bytes, scale 0.1 deg
    info_temp2 = db.Column(db.DECIMAL(5, 1))  # 2bytes, scale 0.1 deg
    info_temp3 = db.Column(db.DECIMAL(5, 1))  # 2bytes, scale 0.1 deg
    info_pm25 = db.Column(db.Integer)  # 2bytes
    ts = db.Column(db.DateTime)

    def __init__(
            self, mobile, sn,
            stat_gun, stat_lock, stat_charge, stat_run,
            stat_net, stat_battery, stat_work,
            info_temp1, info_temp2, info_temp3,
            info_pm25, ts=None
    ):
        self.mobile = mobile
        self.sn = sn
        self.stat_gun = stat_gun
        self.stat_lock = stat_lock
        self.stat_charge = stat_charge
        self.stat_run = stat_run
        self.stat_net = stat_net
        self.stat_battery = stat_battery
        self.stat_work = stat_work
        self.info_temp1 = info_temp1
        self.info_temp2 = info_temp2
        self.info_temp3 = info_temp3
        self.info_pm25 = info_pm25
        self.ts = ts if ts else datetime.utcnow()


class TerminalChargeStatus(db.Model):
    id = db.Column(db.BigInteger, primary_key=True)
    sn = db.Column(db.String(80), db.ForeignKey('pile.sn'))
    mobile = db.Column(db.String(16))
    info_duration = db.Column(db.Integer)  # in second
    info_charged = db.Column(db.DECIMAL(8, 2))  # 3bytes, scale 0.01kW
    info_current = db.Column(db.DECIMAL(5, 2))  # 2bytes, scale 0.01A
    info_volt = db.Column(db.DECIMAL(5, 2))  # 2bytes, scale 0.05V
    ts = db.Column(db.DateTime)

    def __init__(
            self, mobile, sn,
            info_duration, info_charged, info_current, info_volt,
            ts=None
    ):
        self.mobile = mobile
        self.sn = sn
        self.info_duration = info_duration
        self.info_charged = info_charged
        self.info_current = info_current
        self.info_volt = info_volt
        self.ts = ts if ts else datetime.utcnow()

    def to_json(self):
        attrs = ('id', 'mobile', 'sn', 'info_duration', 'info_charged', 'info_current', 'info_volt', 'ts')
        return {attr: self.__getattribute__(attr) for attr in attrs}


class TerminalImage(db.Model):
    id = db.Column(db.BigInteger, primary_key=True)
    version = db.Column(db.Integer, nullable=False)
    base = db.Column(db.Integer, nullable=False)
    hexfile = db.Column(db.LargeBinary(length=256 * 1024), nullable=False)
    hexmd5 = db.Column(db.String(32), nullable=False)
    binfile = db.Column(db.LargeBinary(length=256 * 1024), nullable=True)
    binmd5 = db.Column(db.String(32), nullable=False)
    upload_time = db.Column(db.DateTime())

    def __init__(self, ts=None):
        self.upload_time = ts if ts else datetime.utcnow()

    def to_dict(self):
        attr = ('base', 'version', 'hexfile', 'binfile', 'hexmd5', 'binmd5')
        d = {k: getattr(self, k) for k in attr}
        d['upload_time'] = to_ts(self.upload_time)
        return d

    def to_json(self):
        # attrs = ('base', 'version', 'hexfile', 'binfile', 'hexmd5', 'binmd5')
        attrs = ('base', 'version', 'hexmd5', 'binmd5', 'id')
        json = {attr: self.__getattribute__(attr) for attr in attrs}
        if self.upload_time is not None:
            json['upload_time'] = self.upload_time.strftime('%Y-%m-%d %H:%M:%S')
        return json
