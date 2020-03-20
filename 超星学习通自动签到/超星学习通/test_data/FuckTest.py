import requests
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer
import re
from time import time
import json

key = "xxxxxxxxx"
s = Serializer(key)
data = {"phone": "xxxxxxxxxxx", "timstp": int(time())}
# 加密
m = s.dumps(data)
ms = re.findall(r"b'(.*)'", str(m))[0]
res = json.loads(requests.post("http://xxxxxxxxxxxxx/PTO", data={"data": ms}).content.decode())
print(res)

if res['status'] == False:
    print("**********************")
