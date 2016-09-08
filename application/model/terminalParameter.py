from .. import db
import json


class TerminalParameter(db.Model):
    id = db.Column(db.Integer, primary_key=True)  # 主键
    type = db.Column(db.String(80))  # 参数修改对应的协议类型
    param = db.Column(db.Text)  # 被修改参数编码为JSON
    pile_sn = db.Column(db.String(80), db.ForeignKey('pile.sn'))  # 被设置的终端桩号，pile表中的sn列
    # pile_sn = db.Column(db.String(80))  # 被设置的终端桩号，pile表中的sn列
    timestamp = db.Column(db.DateTime)  # 触发参数修改的时间戳
    status = db.Column(db.Integer)  # 参数修改尚未完成0、参数修改成功1、参数被拒绝2
    complete_timestamp = db.Column(db.DateTime)  # 完成修改的时间戳
    version = db.Column(db.String(20))  # 版本号 自动产生

    def __init__(self, type=None, param=None, pile_sn=None, timestamp=None, status=None, complete_timestamp=None):
        self.type = type
        self.param = param
        self.pile_sn = pile_sn
        self.timestamp = timestamp
        self.status = status
        self.complete_timestamp = complete_timestamp

    def to_json(self):
        attrs = (
            'id', 'type', 'pile_sn', 'status', 'version')
        ret = {attr: self.__getattribute__(attr) for attr in attrs}
        if self.param:
            ret["param"] = json.loads(self.param)
        if self.timestamp:
            ret['timestamp'] = self.timestamp.strftime('%Y-%m-%d %H:%M:%S')
        if self.complete_timestamp:
            ret['complete_timestamp'] = self.complete_timestamp.strftime('%Y-%m-%d %H:%M:%S')
        return ret
