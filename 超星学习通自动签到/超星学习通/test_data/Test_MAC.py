import json

import requests
import uuid
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer
import re
import time

key = "xxxxxxxxxxx"
s = Serializer(key)

node = uuid.getnode()
mac = uuid.UUID(int=node).hex[-12:]
stp = {"mac": mac, "timstp": int(time.time())}
m = s.dumps(stp)
ms = re.findall(r"b'(.*)'", str(m))[0]

res = json.loads(requests.post("http://xxxxxxxxxxxxxx/CM", data={"data": ms}).content.decode())
try:
    datap = s.loads(res['data'])
    if int(time.time()) - datap['timstp'] < 3:
        if datap['status'] == True:
            date = 7 * 3600 * 24
            s = Serializer(key, date)
            stp = {"Expiration_date": date, "timestp": int(time.time())}
            m = s.dumps(stp)
            ms = re.findall(r"b'(.*)'", str(m))[0]
            print('''
=======================================================================================

        免费Token申请成功，【 注意：】在 config.ini中填写的时候，请保证口令为一行
        
        下面便是已申请的 Token

========================================================================================
            ''')
            print(ms)
            time.sleep(600)
        else:
            print('''
=======================================================================================

            向服务器所求 Token 口令失败，因：用户已经领取过一次免费的Token了

========================================================================================
            ''')
            time.sleep(600)
except Exception as e:
    print('''
=======================================================================================

                            非法回复，不是服务器发来的消息

========================================================================================
    ''')
    time.sleep(600)
