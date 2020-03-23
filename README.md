# 学习通自动签到系统（秒懂签到）
**其实，本来打算把签到系统一直压着，赚点饭钱，可是仔细想了想，还是算了吧，也未必有人会来买，更何况就算有人买，也就赚点小钱8，平时还需要服务器维护，并且我免费的学生服务器就一年时间。。。。。反正就是巴拉巴拉一堆问题，不如把源码公开后放到博客里，也算是记录了大学期间的一件趣事8**

**下载的方式：**
- [**github下载（源码）**](https://github.com/Meterprete/Learning-pass-automatic-sign-in-system)
- **[【2020.3.23更新】腾讯微云下载，成品，无源码，可直接使用（提取码：54250p）](https://share.weiyun.com/5t1fs6I)**

> 首先说，实现学习通的签到功能并不难（包括手势签到扫码签到什么什么的），自己可以抓包找找接口，实在找不到或者嫌麻烦，也可以用我项目里的这几个接口也可以。这里要说的是，其实让我印象最深刻的是第一次做验证系统（就是。。。。软件使用权限口令的生成，怎么防止第三方解密，以及如何防止用户二次利用Token，以及怎么防止用户修改本地时间达到延长软件使用期限，还有防止在软件和服务器通信过程中第三方劫持，限制同一台机器使用一个Token，并且还要考虑用户如果在Token没有失效的情况下再次购买Token，服务器不能因为MAC和Token不一样就限制人家吧，还有得防止恶意请求DDOS你的服务器8。。。。。。反正就是巴拉巴拉一大堆需要考虑的问题，不过还好都解决了，完成的不是很困难）
0
> **下面就写一下解决这些问题的大体思路8：** 首先是从防止第三方恶意请求你的服务器，这个其实考虑过用redis来做，不过。。。。原谅我，没有用redis挡在前面，我缓解数据库压力的方法，采用的是逻辑判断的方法。就是限定发送的POST请求传递过来的数据是我指定的口令加密的数据，并且为了保证对方使用相同的传递的数据发起恶意攻击，还需要每一个传递过来的数据都是唯一的，并且都是某一时刻以后不能重复或者失效的，这里我是用的就是，把数据和时间戳绑定，解密数据后，只需要客户端的时间戳和当前服务器的时间戳的差值即可，这里涉及到传输延迟，所以，判断差值的时候我故意让他最大传输时延为3秒，然后如果满足条件，就基本可以断定是客户端发来的数据。在这之后，就是要判断客户端的Token是否绑定的是他绑定的MAC，其次还要判断用户密码是否已修改以及用户是否购买的新的口令来更新原来的信息。如下所示，是加密和解密以及进行用户身份判定的过程，加密没想到更好的，就直接用的`itsdangerous`
```python
‘’‘数据加密与绑定’‘’
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer
import re
def xxx():
	key = "xxxxxxxxxxxxx"
	s = Serializer(key)
	stp = {'timestp': int(time.time()), 'phone': phone, 'pwd': pwd, 'mac': mac,
	       'token': token}
	m = s.dumps(stp)
	ms = re.findall(r"b'(.*)'", str(m))[0]
	msg = {'data': ms}
	res = requests.post("http://xxxxxxxxxxx/conn_check", data=msg)
	return res

‘’‘服务器端数据的解密以及用户身份的判定’‘’
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer
key = "xxxxxxxxxxxxxx"
s = Serializer(key)
def post(self,response)
	try:
	   timestp_server = int(time())
	   res = s.loads(response.POST.get('data'))
	   # 确保3秒之内传到服务器
	   if (timestp_server - res['timestp']) < 3:
	       print("server: {}".format(timestp_server))
	       print("user: {}".format(res['timestp']))
	       print("cha: {}".format(timestp_server - res['timestp']))
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
```
当然，这里服务器返回的数据没有加密，不过不得不考虑到中间被挟持，然后发送假请求给客户端的情况，加密这里，我是在用户获取7天免费试用期限获取Token的时候加密的。

> **然后，再来说一说，获取7天使用权限生成的Token的时候，我考虑了什么**
> 其实过程和上面差不多，只不过，这里需要限制的是用户的MAC地址。所以，比较容易想到的是，如果用户之前登陆过，数据库里肯定由用户的MAC信息，所以，就不难想到，当用户想要获取对软件的7天使用权限的时候，只需要判断用户的MAC是否已经存在数据库即可。可是，这里就要考虑到，如果服务器返回的数据过于简单，会被第三方劫持利用，所以，必须对服务器返回的数据进行加密，客户端的判断方法和上面说的服务器的判断方法差不多，进行时间戳和消息绑定，这样就保证了客户端接收到的数据唯一性，客户端可以对时间戳判断，如果是3秒之内发送过来的数据，就接收，如果不是，就直接抛异常，下面就是新用户免费领取7天软件使用权限的客户端以及服务器的代码：

```python
‘’‘服务器端’‘’
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
              data = {'status': True, 'timstp': int(time())}
              resp = re.findall(r"b'(.*)'", str(s.dumps(data)))[0]
              return JsonResponse({"data": resp})
      else:
          return JsonResponse({'status': 'Network reason request timeout, error'})
  except:
      return JsonResponse({'status': 'Request unofficial, error'})




‘’‘客户端’‘’
import json

import requests
import uuid
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer
import re
import time

key = "xxxxxxxxx"
s = Serializer(key)

node = uuid.getnode()
mac = uuid.UUID(int=node).hex[-12:]
stp = {"mac": mac, "timstp": int(time.time())}
m = s.dumps(stp)
ms = re.findall(r"b'(.*)'", str(m))[0]

res = json.loads(requests.post("http://xxxxxxxx/CM", data={"data": ms}).content.decode())
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

```
> 下面，是大体签到代码的实现，不难实现，就不多说了，其中去除了一些敏感信息。

```python
import multiprocessing
import requests
import json
import smtplib
from email.mime.text import MIMEText
import time
import re
import base64
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer
import uuid
from multiprocessing import Process


class Baopo:
    def __init__(self):

        '''读取配置文件中的配置信息'''
        with open('config.ini', 'r') as f:
            self.config = json.loads(f.read())

        '''邮件信息初始化'''
        self.sender = 'xxxxxx@163.com'
        self.password = 'xxxxxxxxxxxxx'
        self.sendTo = self.config['sendTo']
        self.mail_host = "smtp.163.com"
        try:
            # 获取时间戳以及约定的时间
            self.Time = self.config['Token']
            s = Serializer("xxxxxxxxxxxx")
            self.epc = s.loads(self.Time)['Expiration_date']
            self.startime = int(s.loads(self.Time)['timestp'])
        except:
            print('''
====================================================================================

    程序无法正常运行，因为您的使用期限已到，请向开发者购买Token后继续使用。

    价格规则：【7天/2块钱】（2块钱使用7天）
    
    开发者行寒窗苦读20载，开发软件8容易啊，哥哥姐姐们赏口饭吃吧（跪谢）
    开发者还跑着服务器，高昂的费用使得苦逼的开发者几乎去要饭
    8行啦，哥哥姐姐们再8赏口饭吃就真的要去桥下打地铺啦，可怜可怜苦逼的开发者8

    开发者微信：weichat0007

===================================================================================== 
            ''')
            return

        # 请求标准时间
        standerd_url = "http://api.k780.com:88/?app=life.time&appkey=10003&sign=b59bc3ef6191eb9f747dd4e83c99f2a4&format=json"
        self.timep = int(json.loads(requests.get(standerd_url).content.decode())['result']['timestamp'])
        # 获取网卡的MAC地址
        node = uuid.getnode()
        self.mac = uuid.UUID(int=node).hex[-12:]

        '''学习通接口相关信息初始化'''
        self.Signin_url = "https://mobilelearn.chaoxing.com/pptSign/stuSignajax?activeId={}&uid={}&clientip=&latitude=-1&longitude=-1&appType=15&fid={}"
        self.actived_url = "https://mobilelearn.chaoxing.com/ppt/activeAPI/taskactivelist?courseId="
        self.getclass_url = "http://mooc1-api.chaoxing.com/mycourse/backclazzdata?view=json&rss=1"
        self.index_url = "http://i.mooc.chaoxing.com/space/index?"
        self.login_url = "https://passport2.chaoxing.com/fanyalogin"
        self.login_data = {
            "fid": "-1",
            "uname": self.config['username'],
            'refer': 'http://fxlogin.chaoxing.com/findlogin.jsp?backurl=http://www.chaoxing.com/channelcookie',
            "password": re.findall(r"b'(.*)'", str(base64.b64encode(self.config['password'].encode())))[0],
            "t": "true"
        }

        # 伪造请求头
        self.headers = {
            "Referer": "https://passport2.chaoxing.com/login?fid=&newversion=true&refer=http://fxlogin.chaoxing.com/findlogin.jsp?backurl=http://www.chaoxing.com/channelcookie",
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.132 Safari/537.36"
        }

    # 传入 课程名 / 教师姓名 / 签到时间 / 学生人数 / 签到形式 / 剩余签到时间
    def send_email(self, className, teacherName, localTime, stuSum, signKind, Remaining_time):
        receiver = []
        content = '''
        <div style="width: 300px;margin: auto;"><h1 style="color: mediumseagreen;font-family: 楷体;">秒懂签到 世界如此简单</h1><div style="font-family: 楷体;"><div style="font-size: 10px">            尊敬的用户您好:<br>            &nbsp;&nbsp;&nbsp;&nbsp;刚刚由<span style="color: red">{}</span> 老师发起的签到任务已帮您签到成功，签到系统仍然继续为您监测签到任务.            '秒懂签到'，用技术改变时代生活节奏<br><br></div><div style="width: 300px;border: double 1px green"><div style="text-align: center;padding: 5px"><div style="width: 270px;"><table style="text-align: right"><tr><span style="color: mediumseagreen;font-weight: bolder">签到成功</span></tr><tr><td>√</td><td>&nbsp;</td><td style="font-size: 10px">课程名称</td><td style="text-align: left;font-size: 9px;font-weight: bolder">：{}</td></tr><tr><td>√</td><td>&nbsp;</td><td style="font-size: 10px">完成时间</td><td style="text-align: left;font-size: 9px;font-weight: bolder">：{}</td></tr><tr><td>√</td><td>&nbsp;</td><td style="font-size: 10px">签到类型</td><td style="text-align: left;font-size: 9px;font-weight: bolder">：{}</td></tr><tr><td>√</td><td>&nbsp;</td><td style="font-size: 10px">教师姓名</td><td style="text-align: left;font-size: 9px;font-weight: bolder">：{}</td></tr><tr><td>√</td><td>&nbsp;</td><td style="font-size: 10px">课堂人数</td><td style="text-align: left;font-size: 9px;font-weight: bolder">：{}</td></tr><tr><td>√</td><td>&nbsp;</td><td style="font-size: 10px">剩余时间</td><td style="text-align: left;font-size: 9px;font-weight: bolder">：{}</td></tr></table></div></div><br></div><p></p><a style="font-weight: bolder;font-family: '宋体';color: crimson;text-decoration: none" target="_blank"           href="https://blog.csdn.net/weixin_44449518"><div style="background-color: lightgreen;border: 1px solid red;width: 300px;height: 50px;text-align: center;line-height: 50px">                点击链接 秒懂 开发者</div></a></div></div>
        '''.format(teacherName, className, localTime, signKind, teacherName, stuSum, Remaining_time)
        title = '老师发起的签到任务已自动签到成功'
        message = MIMEText(content, 'html', 'utf-8')
        receiver.append(self.sendTo)
        message['From'] = "秒懂签到系统 <{}>".format(self.sender)
        message['To'] = ",".join(receiver)
        # print(message['To'])
        message['Subject'] = title

        try:
            smt = smtplib.SMTP_SSL(self.mail_host, 465)
            smt.login(self.sender, self.password)
            smt.sendmail(self.sender, receiver, message.as_string(), )
            print('''
=====================================
||                                 ||
            邮件发送成功
        {} 
||                                 ||
=====================================
            '''.format(localTime))
        except smtplib.SMTPException as e:
            print(e)
            print("邮件发送失败！！！")

    def todo(self):
        '''获取cookies'''
        s = requests.Session()
        try:
            s.post(url=self.login_url, headers=self.headers, data=self.login_data)
            class_list_html = s.get(self.getclass_url, headers=self.headers).content.decode()
            class_list_dict = json.loads(class_list_html)['channelList']
            from tts import Test_check
            check = Test_check()
            res = json.loads(check.run(token=self.Time, phone=self.config['username'], pwd=self.config['password'],
                                       mac=self.mac).content.decode())
            if res['status'] != 'True':
                print('''
====================================================

    {}

====================================================
                '''.format(res['status']))
                return

        except Exception as e:
            print(e)
            print('''
=====================================

    用户名或密码错误，登录失败
    
=====================================
            ''')
            return

        courseId = []
        classId = []
        className = []
        teacherName = []
        stuSum = []
        uid = s.cookies['UID']
        fid = s.cookies['fid']

        '''对 uid classId courseId 进行初始化'''
        for temp in class_list_dict:
            try:
                courseId.append(temp['content']['course']['data'][0]['id'])
            except Exception as e:
                continue
            classId.append(temp['key'])
            className.append(temp['content']['course']['data'][0]['name'])
            teacherName.append(temp['content']['course']['data'][0]['teacherfactor'])
            stuSum.append(temp['content']['studentcount'])

        '''进行课程列表的获取'''
        count = 0
        print("=" * 150 + "\n")
        for name in className:
            if ((count + 1) % 3 == 0):
                if count == len(className) - 1:
                    print("【{}】".format(count) + name, end="")
                else:
                    print("【{}】".format(count) + name, end="\n")
            else:
                if count == len(className) - 1:
                    print("【{}】".format(count) + name, end="")
                else:
                    print("【{}】".format(count) + "%-30s" % name, end="\t\t\t")
            count = count + 1
        print("\n" + "=" * 150)
        task_list_str = input("请输入要检测的课程前面'【】'中的序号，多个课程之间用【空格】隔开：(例如：4 5 10)\n")
        task_list = task_list_str.split(" ")

        '''内置程序启动'''
        from luping import Run
        r = Run()
        p1 = Process(target=r.todo)
        p1.start()

        while True:
            '''进行课程任务列表的获取，判断是否有签到任务，如果有就完成签到'''
            for i in range(len(classId)):
                if str(i) in task_list:
                    json_active = s.get(
                        self.actived_url + str(courseId[i]) + "&classId=" + str(classId[i]) + "&uid=" + uid,
                        headers=self.headers).content.decode()
                    # print(self.actived_url + str(courseId[i]) + "&classId=" + str(classId[i]) + "&uid=" + uid)
                    # https: // mobilelearn.chaoxing.com / ppt / activeAPI / taskactivelist?courseId = 210811209 & classId = 22346919 & uid = 79654370

                    try:
                        res = json.loads(json_active)
                    except:
                        continue
                    activeList = res['activeList']

                    for j in range(len(activeList)):
                        if 'url' in activeList[j].keys() and 'activePrimaryId' in activeList[j]['url']:
                            if activeList[j]['activeType'] == 2 and activeList[j]['status'] == 1:
                                activeId = activeList[j]['id']
                                signKind = activeList[j]['nameOne']
                                Remaining_time = activeList[j]['nameFour']
                                msg = s.get(self.Signin_url.format(activeId, uid, fid),
                                            headers=self.headers).content.decode()
                                if msg == "您已签到过了":
                                    continue
                                else:
                                    localTime = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
                                    print('''
=====================================
||                                 ||
               签到成功 
         {}
||                                 ||
=====================================
                                    '''.format(localTime))
                                    # send_email(self, className, teacherName, localTime, stuSum, signKind)
                                    self.send_email(className[i], teacherName[i], localTime, stuSum[i], signKind,
                                                    Remaining_time)
            print("本次检测结束，1分钟后任务重新启动")
            time.sleep(60)

    def run(self):
        end = self.startime + self.epc
        if end >= self.timep:
            print('''
========================================================================================

        您的使用时间还剩 {} 小时 {} 分钟 {} 秒，以免影响您的正常使用
        请联系开发者购买更多使用时间

    开发者行寒窗苦读20载，开发软件8容易啊，哥哥姐姐们赏口饭吃吧（跪谢）
    开发者还跑着服务器，高昂的费用使得苦逼的开发者几乎去要饭
    8行啦，哥哥姐姐们再8赏口饭吃就真的要去桥下打地铺啦，可怜可怜苦逼的开发者8

        价格规则：【7天/2块钱】（2块钱使用7天）

        开发者微信：weichat0007

=========================================================================================
            '''.format(int((end - self.timep) / 3600), int(((end - self.timep) % 3600) / 60),
                       int(((end - self.timep) % 3600) % 60)))
            try:
                self.todo()
            except Exception as e:
                print(e)
                print("请检查配置文件 config.ini中 的个人信息是否填写完整，若在填写正确的情况下报错，请联系（QQ：358297574）")
        else:
            print('''
====================================================================================

    程序无法正常运行，因为您的使用期限已到，请向开发者购买Token后继续使用。

    价格规则：【7天/2块钱】（2块钱使用7天）
    
    开发者行寒窗苦读20载，开发软件8容易啊，哥哥姐姐们赏口饭吃吧（跪谢）
    开发者还跑着服务器，高昂的费用使得苦逼的开发者几乎去要饭
    8行啦，哥哥姐姐们再8赏口饭吃就真的要去桥下打地铺啦，可怜可怜苦逼的开发者8

    开发者微信：weichat0007

=====================================================================================
            ''')


if __name__ == '__main__':
    multiprocessing.freeze_support()
    print('''
==================================================================================
||
||	 【1】 Name of the project: 秒懂签到系统
||
||	 【2】              author: Caiden_Micheal
||
||	 【3】      GitHub address: https://github.com/Meterprete?tab=repositories
||
||	 【4】    Personal mailbox: wangxinqhou@foxmail.com
||
||	           			  time: 2020.3.17
||
==================================================================================
            ''')
    print('''
=====================================

        请稍等，系统正在初始化中

=====================================
            ''')
    bopo = Baopo()
    try:
        bopo.run()
    except:
        print('''
=====================================

            程序异常终止

=====================================
        ''')
        time.sleep(600)

```

> 当然，上面说的只不过是整个项目中的冰山一角，整个项目的实现难度为 中，除了可以说出来的这些，还有一些不为人知代码藏在项目里，可以自取慢慢研究8，就说到这里了。说多了浪费时间，不如自己拿去研究研究。

**新用户成功申请获得免费Token截图：**![在这里插入图片描述](https://img-blog.csdnimg.cn/20200320193246348.png?x-oss-process=image/watermark,type_ZmFuZ3poZW5naGVpdGk,shadow_10,text_aHR0cHM6Ly9ibG9nLmNzZG4ubmV0L3dlaXhpbl80NDQ0OTUxOA==,size_16,color_FFFFFF,t_70)
**重复使用新用户的Token提醒**![在这里插入图片描述](https://img-blog.csdnimg.cn/20200320193354897.png?x-oss-process=image/watermark,type_ZmFuZ3poZW5naGVpdGk,shadow_10,text_aHR0cHM6Ly9ibG9nLmNzZG4ubmV0L3dlaXhpbl80NDQ0OTUxOA==,size_16,color_FFFFFF,t_70)
**正常运行截图：**![在这里插入图片描述](https://img-blog.csdnimg.cn/20200320193518184.png?x-oss-process=image/watermark,type_ZmFuZ3poZW5naGVpdGk,shadow_10,text_aHR0cHM6Ly9ibG9nLmNzZG4ubmV0L3dlaXhpbl80NDQ0OTUxOA==,size_16,color_FFFFFF,t_70)
**获取到签到任务签到成功截图：**![在这里插入图片描述](https://img-blog.csdnimg.cn/20200320193801367.png?x-oss-process=image/watermark,type_ZmFuZ3poZW5naGVpdGk,shadow_10,text_aHR0cHM6Ly9ibG9nLmNzZG4ubmV0L3dlaXhpbl80NDQ0OTUxOA==,size_16,color_FFFFFF,t_70)
**邮件接收通知截图：**![在这里插入图片描述](https://img-blog.csdnimg.cn/20200320193936716.png?x-oss-process=image/watermark,type_ZmFuZ3poZW5naGVpdGk,shadow_10,text_aHR0cHM6Ly9ibG9nLmNzZG4ubmV0L3dlaXhpbl80NDQ0OTUxOA==,size_16,color_FFFFFF,t_70)


**下载的方式：**
- [**github下载（源码）**](https://github.com/Meterprete/Learning-pass-automatic-sign-in-system)
- **[【2020.3.23更新】腾讯微云下载，成品，无源码，可直接使用（提取码：54250p）](https://share.weiyun.com/5t1fs6I)**
