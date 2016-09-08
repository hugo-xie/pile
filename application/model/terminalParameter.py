from .. import db
import json


class TerminalParameter(db.Model):
    id = db.Column(db.Integer, primary_key=True)  # ����
    type = db.Column(db.String(80))  # �����޸Ķ�Ӧ��Э������
    param = db.Column(db.Text)  # ���޸Ĳ�������ΪJSON
    pile_sn = db.Column(db.String(80), db.ForeignKey('pile.sn'))  # �����õ��ն�׮�ţ�pile���е�sn��
    # pile_sn = db.Column(db.String(80))  # �����õ��ն�׮�ţ�pile���е�sn��
    timestamp = db.Column(db.DateTime)  # ���������޸ĵ�ʱ���
    status = db.Column(db.Integer)  # �����޸���δ���0�������޸ĳɹ�1���������ܾ�2
    complete_timestamp = db.Column(db.DateTime)  # ����޸ĵ�ʱ���
    version = db.Column(db.String(20))  # �汾�� �Զ�����

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
