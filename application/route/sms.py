import httplib2
import urllib
from .helper import get_setting
from ..const import SettingKey, ErrNo
from .. import app


class SMS:
    """
    This class uses third party service to send SMS.
    Parameters:
        mobile: mobile number
        msg: message
    Errors:
        SMS: failure of sending SMS
    """
    _sign = ''
    _url = 'http://sms.1xinxi.cn/asmx/smsservice.aspx'

    @staticmethod
    def _post(url, params):
        app.logger.info('SMS API param8s: %r', params)
        data=urllib.parse.urlencode(params)
        app.logger.info('encoded SMS params: %r', data)
        h=httplib2.Http()
        headers={'Content-type': 'application/x-www-form-urlencoded; charset=UTF-8'}
        try:
            (resp_headers, content)=h.request(url, "POST", headers=headers, body=data)
            return content.decode()
        except httplib2.HttpLib2Error as e:
            if app.debug:
                app.logger.exception(e)
            return ''

    @classmethod
    def send(cls, mobile, msg):
        sms_name = get_setting(SettingKey.SMS_ACCOUNT)  # '422134981'
        sms_pwd = get_setting(SettingKey.SMS_PASSWORD)  # '0AFA41128360DBB72907E5F0C6D8'
        params = dict(name=sms_name, pwd=sms_pwd, content=msg, sign=cls._sign, type='pt', mobile=mobile)
        content = cls._post(cls._url, params)
        if not content.startswith('0,'):
            app.logger.error('unexpected reply from sms gw: %r', content)
            return ErrNo.SMS
        return ErrNo.OK


