from django.shortcuts import render
import re
from django.views import View
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer
from django.http import JsonResponse
from time import time
from TemConn.models import UserMac
import json

key = "加密密钥"
s = Serializer(key)


class check(View):
    def get(self, response):
        return JsonResponse({'status': "Nima blew up. Request P. request. Request way. NIMA's wrong. Fuck"})

    def post(self, response):
        try:
            timestp_server = int(time())
            res = s.loads(response.POST.get('data'))
            # 确保3秒之内传到服务器
            if (timestp_server - res['timestp']) < 3:
                token = res['token']
                # 判断token是否存在数据库（是否被使用过）
                try:
                    UM = UserMac.objects.get(token=token)
                    # 如果被使用过，就判断是否是同一个人（mac地址判断）
                    if UM.mac == res['mac']:
                        # 如果密码不同，说明人家改密码了，数据库也需要修改
                        if UM.password != res['pwd']:
                            UM.password = res['pwd']
                            UM.save()
                            return JsonResponse({'status': 'True'})
                        else:
                            return JsonResponse({'status': 'True'})
                    else:
                        return JsonResponse({'status': 'Bound MAC address is not local Mac, error'})

                # 如果Token没被用过，判断手机号是否存在数据库
                except Exception as e:
                    try:
                        UM2 = UserMac.objects.get(phone=res['phone'])
                        # 用户是来更新数据的
                        UM2.password = res['pwd']
                        UM2.mac = res['mac']
                        UM2.token = token
                        UM2.save()
                        return JsonResponse({'status': 'True'})

                    except:
                        # 如果手机号不存在数据库中，说明用户第一次注册，直接向数据库写数据
                        usermac = UserMac()
                        usermac.token = token
                        usermac.phone = res['phone']
                        usermac.password = res['pwd']
                        usermac.mac = res['mac']
                        usermac.photo = False
                        usermac.save()
                        return JsonResponse({'status': 'True'})
            else:
                return JsonResponse({'status': 'Network reason request timeout, error'})
        except Exception as e:
            print(e)
            return JsonResponse({'status': 'Request unofficial, error'})


class PTO(View):
    def get(self, response):
        return JsonResponse({'status': "Nima blew up. Request P. request. Request way. NIMA's wrong. Fuck"})

    def post(self, response):
        try:
            data = response.POST.get('data')
            res = s.loads(data)
            timstp = res['timstp']
            if (time() - timstp) < 3:
                phone = res['phone']
                um = UserMac.objects.get(phone=phone)
                photo = um.photo
                return JsonResponse({'status': photo})
            else:
                return JsonResponse({'status': 'Network reason request timeout, error'})
        except:
            return JsonResponse({'status': 'Request unofficial, error'})


class CM(View):
    def get(self, response):
        return JsonResponse({'status': "Nima blew up. Request P. request. Request way. NIMA's wrong. Fuck"})

    def post(self, response):
        try:
            data = response.POST.get('data')
            res = s.loads(data)
            timstp = res['timstp']
            if (time() - timstp) < 3:
                mac = res['mac']
                try:
                    UserMac.objects.get(mac=mac)
                    data = {'status': 'Request unofficial, error', 'timstp': int(time())}
                    resp = re.findall(r"b'(.*)'", str(s.dumps(data)))[0]
                    return JsonResponse({'data': resp})
                except:
                    date = 7 * 3600 * 24
                    sm = Serializer(key, date)
                    stp = {"Expiration_date": date, "timestp": int(time())}
                    m = sm.dumps(stp)
                    ms = re.findall(r"b'(.*)'", str(m))[0]
                    data = {'status': True, 'timstp': int(time()), 'token': ms}

                    resp = re.findall(r"b'(.*)'", str(sm.dumps(data)))[0]
                    return JsonResponse({"data": resp})
            else:
                return JsonResponse({'status': 'Network reason request timeout, error'})
        except Exception as e:
            print(e)
            return JsonResponse({'status': 'Request unofficial, error'})
