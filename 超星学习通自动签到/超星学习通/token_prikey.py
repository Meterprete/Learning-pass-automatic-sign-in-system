from itsdangerous import TimedJSONWebSignatureSerializer as Serializer
import re
import time

key = "xxxxxxx"
date = int(input("请输入预计用户开通软件的使用期限(xx天，例如输入数字3，代表3天)：\n")) * 3600 * 24
s = Serializer(key, date)
stp = {"Expiration_date": date, "timestp": int(time.time())}
m = s.dumps(stp)
ms = re.findall(r"b'(.*)'", str(m))[0]
print(ms)
