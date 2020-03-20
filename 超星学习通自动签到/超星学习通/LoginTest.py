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
        self.password = 'xxxxxxxxx'
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
