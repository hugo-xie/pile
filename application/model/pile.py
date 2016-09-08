from .. import db
from .helper import to_ts
from .terminal import Terminal, TerminalInfo
from datetime import datetime


class Pile(db.Model):
    """
    This class defines pile structure.

    id : record id
    sn : pile serial number
    name : pile name
    longitude : longitude
    latitude : latitude
    address : pile address
    auto_ack : whether the pile automatically accepts application
    electricity : electricity fee
    service : service fee
    appointment : appointment fee
    open : open time
    close : close time
    auto_ack_start : the start timestamp if the pile accepts the application automatically
    auto_ack_end : the end timestamp if the pile accepts the application automatically
    man_ack_secs : the total seconds of the interval between application and manual acknowledge
    man_ack_times : the times of manual acknowledge
    owner_id : owner id
    supported : <TODO>
    locked_by : <TODO>
    started_by : <TODO>
    time_slots : the booked time slot list
    books : book history
    status_history : <TODO>
    info_history : <TODO>
    """
    id = db.Column(db.Integer, primary_key=True)
    sn = db.Column(db.String(80), unique=True, nullable=False, index=True)
    name = db.Column(db.String(80), nullable=False, unique=True)
    longitude = db.Column(db.Numeric(16, 13), nullable=False)
    latitude = db.Column(db.Numeric(16, 13), nullable=False)
    address = db.Column(db.String(80))
    auto_ack = db.Column(db.Integer, nullable=False)
    electricity = db.Column(db.Numeric(10, 2), nullable=False)
    service = db.Column(db.Numeric(10, 2), nullable=False)
    appointment = db.Column(db.Numeric(10, 2), nullable=False)
    open = db.Column(db.Time, nullable=False)
    close = db.Column(db.Time, nullable=False)
    auto_ack_start = db.Column(db.DateTime)
    auto_ack_end = db.Column(db.DateTime)
    man_ack_secs = db.Column(db.Integer)
    man_ack_times = db.Column(db.Integer)

    owner_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    supported = db.Column(db.Integer)
    locked_by = db.Column(db.Integer, db.ForeignKey('book.id'))
    started_by = db.Column(db.Integer, db.ForeignKey('book.id'))
    time_slots = db.relationship('PileTimeSlot', backref='pile', lazy='dynamic')
    books = db.relationship('Book', backref='pile', lazy='dynamic', primaryjoin="Pile.id==Book.pile_id")
    status_history = db.relationship('Terminal', backref='pile', lazy='dynamic')
    info_history = db.relationship('TerminalInfo', backref='pile', lazy='dynamic')

    # add column
    create_time = db.Column(db.DateTime)  # 新建时间
    voltage = db.Column(db.Numeric(10, 2), nullable=True)  # 电压
    temperature = db.Column(db.Numeric(10, 2), nullable=True)  # 温度，可为空
    pm = db.Column(db.Numeric(10, 2), nullable=True)  # PM值，可为空
    is_charging = db.Column(db.Boolean)  # 是否正在充电，可为空，建议新建一张表
    can_book = db.Column(db.Boolean, nullable=True)  # 是否可预约
    is_available = db.Column(db.Boolean)  # 是否可用
    software_version = db.Column(db.String(80))  # 软件版本号
    last_maintain_time = db.Column(db.DateTime)  # 上次维护时间
    next_maintain_time = db.Column(db.DateTime)  # 下次维护时间
    maintain_description = db.Column(db.Text)  # 维护描述
    is_qualified = db.Column(db.Boolean)  # 是否合格
    is_deleted = db.Column(db.Boolean)  # 是否已被删除

    upgrade_status = db.Column(db.SmallInteger)  # 升级状态
    configuration_status = db.Column(db.SmallInteger)  # 配置状态
    upgrade_rate = db.Column(db.Numeric(10, 3))  # 升级进度
    configuration_rate = db.Column(db.Numeric(10, 3))  # 配置进度


    # add relationship with terminal parameter
    terminalParameters = db.relationship('TerminalParameter', backref='pile', lazy='dynamic')

    # def __init__(self, name, sn, longitude, latitude, address, auto_ack, electricity, service, appointment, open, close,
    # 			 owner_id, auto_ack_start=None, auto_ack_end=None, supported=1):
    # 	self.name = name
    # 	self.sn = sn
    # 	self.longitude = longitude
    # 	self.latitude = latitude
    # 	self.auto_ack = auto_ack
    # 	self.electricity = electricity
    # 	self.service = service
    # 	self.appointment = appointment
    # 	self.open = open
    # 	self.close = close
    # 	self.owner_id = owner_id
    # 	self.auto_ack_start = auto_ack_start
    # 	self.auto_ack_end = auto_ack_end
    # 	self.man_ack_secs = 0
    # 	self.man_ack_times = 0
    # 	self.address = address
    # 	self.supported = supported
    def __init__(self):
        self.name = ""
        self.sn = ""
        self.longitude = "0.0"
        self.latitude = "0.0"
        self.auto_ack = -1
        self.electricity = 0.0
        self.service = 0.0
        self.appointment = 0.0
        self.open = datetime.strptime("00:00:00", "%H:%M:%S")
        self.close = datetime.strptime("00:00:00", "%H:%M:%S")
        self.owner_id = None
        self.auto_ack_start = None
        self.auto_ack_end = None
        self.man_ack_secs = 0
        self.man_ack_times = 0
        self.address = ""
        self.supported = 1

    def to_json(self):
        attrs = ('id', 'name', 'sn', 'longitude', 'latitude', 'auto_ack', 'electricity', 'service',
                 'appointment', 'owner_id', 'address', 'supported', 'create_time', 'voltage', 'temperature', 'pm',
                 'is_charging', 'can_book',
                 'is_available', 'software_version', 'last_maintain_time', 'next_maintain_time', 'maintain_description',
                 'is_qualified', 'is_deleted', 'upgrade_status', 'upgrade_rate', 'configuration_rate',
                 'configuration_status')
        json = {attr: self.__getattribute__(attr) for attr in attrs}
        json['open'] = to_ts(self.open)
        json['close'] = to_ts(self.close)
        if self.auto_ack_start is not None:
            json['auto_ack_start'] = to_ts(self.auto_ack_start)
        if self.auto_ack_end is not None:
            json['auto_ack_end'] = to_ts(self.auto_ack_end)
        if self.create_time is not None:
            json['create_time'] = self.create_time.strftime('%Y-%m-%d %H:%M:%S')
        if self.last_maintain_time is not None:
            json['last_maintain_time'] = self.last_maintain_time.strftime('%Y-%m-%d %H:%M:%S')
        if self.next_maintain_time is not None:
            json['next_maintain_time'] = self.next_maintain_time.strftime('%Y-%m-%d %H:%M:%S')
        if self.man_ack_times == 0 or self.man_ack_secs is None or self.man_ack_times is None:
            json['mean_man_ack_secs'] = 0
        else:
            json['mean_man_ack_secs'] = self.man_ack_secs / self.man_ack_times

        status = self.status_history.order_by(Terminal.ts.desc()).first()
        if status is None:
            json['online'] = 0
        else:
            json['online'] = status.status

        info = json.setdefault('info', dict())
        pileinfo = (
            self.info_history.order_by(TerminalInfo.ts.desc()).first()
        )
        if pileinfo is None:
            info['pm25'] = '-1'
        else:
            info['pm25'] = int(pileinfo.info_pm25)

        return json
