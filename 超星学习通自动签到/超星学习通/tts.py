import requests
import time
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer
import re


class Test_check:
    # token phone pwd mac
    def run(self, token, phone, pwd, mac):
        key = "15963395653Wx"
        s = Serializer(key)
        stp = {'timestp': int(time.time()), 'phone': phone, 'pwd': pwd, 'mac': mac,
               'token': token}
        m = s.dumps(stp)
        ms = re.findall(r"b'(.*)'", str(m))[0]
        msg = {'data': ms}
        res = requests.post("http://xxxxxxxxx/conn_check", data=msg)
        return res