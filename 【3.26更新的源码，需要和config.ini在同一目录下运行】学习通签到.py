import multiprocessing
import requests
import json
import smtplib
from email.mime.text import MIMEText
import time
import re
import base64


class Baopo:
    def __init__(self):
        self.is_sign = []
        self.task_list = []
        self.alog_list = []
        '''读取配置文件中的配置信息'''
        with open('config.ini', 'rb') as f:
            self.config = json.loads((f.read()).decode())
        '''邮件信息初始化'''
        self.sender = 'wangxinq@163.com'
        self.password = '18853497580Wx'
        self.sendTo = self.config['sendTo']
        self.mail_host = "smtp.163.com"

        '''学习通接口相关信息初始化'''
        self.Signin_url = "https://mobilelearn.chaoxing.com/pptSign/stuSignajax?activeId={}&uid={}&clientip=&appType=15&fid={}&address={}&latitude={}&longitude={}"
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

    def Sign_Kind_test(self, s, activeId, classId, fid, courseId):
        args = "/widget/sign/pcStuSignController/preSign?" + "activeId={}".format(activeId) + "&classId={}".format(
            classId) + "&fid={}".format(fid) + "&courseId={}".format(courseId)
        response = s.get(url="https://mobilelearn.chaoxing.com" + args, headers=self.headers)
        # print("检测链接：https://mobilelearn.chaoxing.com{}".format(args))
        return response

    def upload_img(self, s):
        url = 'https://pan-yz.chaoxing.com/upload?_token=5d2e8d0aaa92e3701398035f530c4155'
        mobile_header = {
            'User-Agent': 'Dalvik/2.1.0 (Linux; U; Android 10; MI 8 MIUI/20.2.27)'
                          ' com.chaoxing.mobile/ChaoXingStudy_3_4.3.6_android_phone_496_27 (@Kalimdor)'
                          '_994222229cb94d688c462b7257600006',
            'Host': 'pan-yz.chaoxing.com'
        }
        img = {}
        try:
            img = {"file": ("Sign.jpg", open("./IMG/M.jpg", "rb"))}
        except:
            print("图片未找到，如果出现了此提示，则说明您未设置拍照签到的图片，已为您发送系统默认的图片，若想自定义照片，请把照片命名为 'M.jpg' 后放在 'IMG' 文件夹中")
            if self.config["gender"] == "男":
                return "9cb266884f96bb598a2ee197268a8baf"
            else:
                return "30f6e2f3c1259aefa7c174f3f379e9cd"
        i_data = {'puid': "80421235"}
        response = s.post(url=url, headers=mobile_header, data=i_data, files=img)
        return response.json().get('objectId')

    def photoSign(self, s, objectId, activeId, courseId, fid):
        """拍照签到"""
        url = "https://mobilelearn.chaoxing.com/pptSign/stuSignajax?activeId={}&classId=&fid={}&courseId={}&objectId={}".format(
            activeId, fid, courseId, objectId)
        response = s.get(url=url, headers=self.headers)
        return response.text

    # 传入 课程名 / 教师姓名 / 签到时间 / 学生人数 / 签到形式 / 剩余签到时间
    def send_email(self, className, teacherName, localTime, stuSum, signKind, Remaining_time, img):
        receiver = []
        if img == "":
            content = '''
<div style="width: 360px;margin: auto;overflow: hidden"><div style="width: 360px;text-align: center"><h1 style="color: mediumseagreen;font-family: 楷体">秒懂签到任务提醒</h1></div><div style="font-family: '楷体';width: 360px;text-align: center;color: red;font-size: 12px;font-weight: bolder">        以免老师察觉到您的不在场，请尽快登录学习通完成本次课堂任务</div><br><div style="font-family: 楷体;"><div style="width: 358px;border: double 1px green;text-align: center"><div style="text-align: center;padding: 5px"><div style="width: 358px;"><table style="height: 180px"><p></p><tr><div style="font-size: 16px;text-align: center;width: 358px;color: mediumseagreen;font-weight: bolder">                                老师刚刚发起了课堂{}</div></tr><tr><td style="width: 60px;font-weight: bolder;font-size: 12px;color: mediumseagreen">√</td><td style="width: 10px">&nbsp;</td><td style="width: 50px;font-size: 12px;color: red;font-weight: bolder;text-align: right">                                课程定位</td><td style=" width: 200px;text-align: left;font-size: 10px;font-weight: bolder"><span                                    style="font-weight: bolder;color: red;text-align: left">：{}</span></td></tr><tr><td style="font-weight: bolder;font-size: 12px;color: mediumseagreen">√</td><td>&nbsp;</td><td style="font-size: 12px;color: red;font-weight: bolder;text-align: right">任务类型</td><td style="text-align: left;font-size: 12px;font-weight: bolder"><span                                    style="font-weight: bolder;color: red;text-align: left">：{}</span></td></tr><tr><td style="font-weight: bolder;font-size: 12px;color: mediumseagreen">√</td><td>&nbsp;</td><td style="font-size: 12px;color: red;font-weight: bolder;text-align: right">教师姓名</td><td style="text-align: left;font-size: 12px;font-weight: bolder"><span                                    style="font-weight: bolder;color: red;text-align: left">：{}</span></td></tr><tr><td style="font-weight: bolder;font-size: 12px;color: mediumseagreen">√</td><td>&nbsp;</td><td style="font-size: 12px;color: red;font-weight: bolder;text-align: right">课堂人数</td><td style="text-align: left;font-size: 12px;font-weight: bolder"><span                                    style="font-weight: bolder;color: red;text-align: left">：{}</span></td></tr><tr><td style="font-weight: bolder;font-size: 12px;color: mediumseagreen">√</td><td>&nbsp;</td><td style="font-size: 12px;color: red;font-weight: bolder;text-align: right">剩余时间</td><td style="text-align: left;font-size: 12px;font-weight: bolder"><span                                    style="font-weight: bolder;color: red;text-align: left">：{}</span></td></tr></table></div></div><br></div><p></p><a style="font-weight: bolder;font-family: '宋体';color: crimson;text-decoration: none" target="_blank"           href="https://blog.csdn.net/weixin_44449518"><div style="background-color: lightgreen;border: 1px solid red;width: 358px;height: 50px;text-align: center;line-height: 50px">                点击链接 秒懂 开发者</div></a></div></div>
                '''.format(signKind, className, signKind, teacherName, stuSum, Remaining_time)
            title = "老师发起新的课堂任务了！！！"
        else:
            content = '''
    <div style="width: 302px;margin: auto;overflow: hidden"><h1 style="color: mediumseagreen;font-family: 楷体">秒懂签到 世界如此简单</h1><div style="font-family: 楷体;"><div style="font-size: 10px">            尊敬的用户您好:<br>            &nbsp;&nbsp;&nbsp;&nbsp;刚刚由<span style="color: red">{}</span> 老师发起的签到任务已帮您签到成功，签到系统仍然继续为您监测签到任务.            '秒懂签到'，用技术改变时代生活节奏<br><br></div><div style="width: 300px;border: double 1px green"><div style="text-align: center;padding: 5px"><div style="width: 270px;"><table style="text-align: right"><tr><span style="color: mediumseagreen;font-weight: bolder">签到成功</span></tr><tr><td>√</td><td>&nbsp;</td><td style="font-size: 10px">课程名称</td><td style="text-align: left;font-size: 9px;font-weight: bolder">：{}</td></tr><tr><td>√</td><td>&nbsp;</td><td style="font-size: 10px">完成时间</td><td style="text-align: left;font-size: 9px;font-weight: bolder">：{}</td></tr><tr><td>√</td><td>&nbsp;</td><td style="font-size: 10px">签到类型</td><td style="text-align: left;font-size: 9px;font-weight: bolder">：{}</td></tr><tr><td>√</td><td>&nbsp;</td><td style="font-size: 10px">教师姓名</td><td style="text-align: left;font-size: 9px;font-weight: bolder">：{}</td></tr><tr><td>√</td><td>&nbsp;</td><td style="font-size: 10px">课堂人数</td><td style="text-align: left;font-size: 9px;font-weight: bolder">：{}</td></tr><tr><td>√</td><td>&nbsp;</td><td style="font-size: 10px">剩余时间</td><td style="text-align: left;font-size: 9px;font-weight: bolder">：{}</td></tr></table></div></div><br></div><p></p><a style="font-weight: bolder;font-family: '宋体';color: crimson;text-decoration: none" target="_blank"           href="https://blog.csdn.net/weixin_44449518"><div style="background-color: lightgreen;border: 1px solid red;width: 300px;height: 50px;text-align: center;line-height: 50px">                点击链接 秒懂 开发者</div></a><p></p><a target="_blank" style="text-decoration: none" href="{}"><div style="border: 1px solid red;background-color: lightgreen;line-height: 30px;width: 300px;height:30px;text-align: center;font-weight: bolder;font-family: '宋体';color: crimson">                拍照签到照片预览</div></a><p></p><a target="_blank" href="{}"><img src="{}"></a></div></div>
            '''.format(teacherName, className, localTime, signKind, teacherName, stuSum, Remaining_time, img, img, img)
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
        except Exception as e:
            print(e)
            print('''
=====================================

    用户名或密码错误，登录失败
    
=====================================
            ''')
            time.sleep(600)
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

        if len(self.task_list) == 0:
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
            # task_list_str = input("请输入要检测的课程前面'【】'中的序号，多个课程之间用【空格】隔开：(例如：4 5 10)\n")
            # self.task_list = task_list_str.split(" ")
            for i in range(len(className)):
                self.task_list.append(str(i))
            print("已选中的课程列表：{}".format(self.task_list))

        while True:
            '''进行课程任务列表的获取，判断是否有签到任务，如果有就完成签到'''
            for i in range(len(classId)):
                if str(i) in self.task_list:
                    json_active = s.get(
                        self.actived_url + str(courseId[i]) + "&classId=" + str(classId[i]) + "&uid=" + uid,
                        headers=self.headers).content.decode()
                    # print(self.actived_url + str(courseId[i]) + "&classId=" + str(classId[i]) + "&uid=" + uid)
                    # mm = "https://mobilelearn.chaoxing.com/ppt/activeAPI/taskactivelist?courseId=210811209&classId=22346890&uid=79654370"
                    try:
                        res = json.loads(json_active)
                    except:
                        continue
                    activeList = res['activeList']
                    if self.config["gender"] == "男":
                        argsp = "9cb266884f96bb598a2ee197268a8baf"
                    else:
                        argsp = "30f6e2f3c1259aefa7c174f3f379e9cd"

                    for j in range(len(activeList)):
                        activeType = activeList[j]['activeType']
                        if activeType == 2 and activeList[j]['status'] == 1:
                            # 判断是否为拍照签到？
                            activeId = activeList[j]['id']
                            if activeId in self.is_sign:
                                continue
                            response = self.Sign_Kind_test(s, activeId, classId[j], fid, courseId[j])
                            signKind = activeList[j]['nameOne']
                            Remaining_time = activeList[j]['nameFour']

                            if re.findall(r'手机拍照', response.text):
                                # 上传拍照照片
                                objectid = self.upload_img(s)
                                # 进行拍照签到
                                msg = self.photoSign(s, objectid, activeId, courseId[j], fid)
                                argsp = objectid

                            elif re.findall(r'签到成功', response.text):
                                print('''
检测到签到任务，签到任务仍未结束，但已却认为您已签到成功，如果看到这句话，那么可以肯定签到任务已完成
但是，不确定是否为本程序完成的普通签到，所以放弃邮件通知（原因，拍照签到和普通签到接口是冲突的，无法
判断是刚完成的普通签到还是之前已完成的其他类型的签到，故放弃通知）
                                ''')
                                self.is_sign.append(activeId)
                                continue


                            else:
                                # 有可能已经签到成功，也有可能为普通签到成功
                                # 位置签到 / 扫码签到等
                                msg = s.get(
                                    self.Signin_url.format(activeId, uid, fid, self.config["address"],
                                                           self.config["latitude"],
                                                           self.config["longitude"],
                                                           ),
                                    headers=self.headers).text
                            if msg == "success":
                                localTime = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
                                print('''
=====================================
||                                 ||
           签到成功 
     {}
||                                 ||
=====================================
                                    '''.format(localTime))
                                img_url = "http://pks3.ananas.chaoxing.com/star3/312_412c/{}.jpg".format(argsp)
                                # send_email(self, className, teacherName, localTime, stuSum, signKind)
                                self.send_email(className[i], teacherName[i], localTime, stuSum[i], signKind,
                                                Remaining_time, img_url)

                        if activeType in [14, 43, 11, 42, 23, 35, 17, 45] and activeList[j]['status'] == 1:
                            if activeList[j]['id'] not in self.alog_list:
                                localTime = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
                                typeACT = ""
                                if activeType == 14:
                                    typeACT = "问卷"
                                if activeType == 43:
                                    typeACT = "投票"
                                if activeType == 11:
                                    typeACT = "选人"
                                if activeType == 42:
                                    typeACT = "测验"
                                if activeType == 23:
                                    typeACT = "评分"
                                if activeType == 35:
                                    typeACT = "分组任务"
                                if activeType == 17:
                                    typeACT = "直播"
                                if activeType == 45:
                                    typeACT = "通知"
                                self.alog_list.append(activeList[j]['id'])
                                print('''
+++++++++++++++++++++++++++++++++++++
++                                 ++
            老师发起{} 
         {}
++                                 ++
+++++++++++++++++++++++++++++++++++++
                                    '''.format(typeACT, localTime))
                                img_url = ""
                                signKind = typeACT
                                Remaining_time = activeList[j]['nameFour']
                                self.send_email(className[i], teacherName[i], localTime, stuSum[i], signKind,
                                                Remaining_time, img_url)

            print("本次检测结束，1分钟后任务重新启动")
            time.sleep(10)

    def run(self):
        while True:
            try:
                self.todo()
            except Exception as e:
                print(e)
                print("‘Remote end closed connection without response’如果看到这一句话，八成是被反爬了，不过不用担心，程序会自动重启")


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
    except Exception as e:
        print(e)
        print('''
=====================================

            程序异常终止

=====================================
        ''')
        time.sleep(600)
