#!/usr/bin/env python
# -*- coding:utf-8 -*-

import os
import mimetypes
import smtplib
from email.header import Header
from email.mime.base import MIMEBase
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.image import MIMEImage
from email import encoders


def send_email(login=None, mail=None, images=None, attachments=None, use_ssl=None):
    """
    发送常规邮件,可以有图片和其它格式的附件

    :param login: dict:登录信息,包括smtp服务器地址,帐号,密码:

    .. code:: python

        {
            'smtpserver': 'smtp.163.com',
            'username': 'xxx@163.com',
            'password': 'xxx'
        }

    :param mail: dict,邮件内容,包含邮件类型,发送人,收件人(多人的话要使用列表),标题,内容:

    .. code:: python

        {
            'email_type': "html",  # 可以是:plain\html
            'from': 'xxx@163.com',
            'to': 'xxx@126.com',
            'subject': "标题",
            'content': "正文"
        }

    :param images: list,图片附件列表(由路径组成)
    :param attachments: list,其它附件列表(由路径组成)
    :param use_ssl: 否使用 ssl(暂时无用0
    :return:
    """

    smtpserver = login.get("smtpserver")
    username = login.get("username")
    password = login.get("password")

    email_type = mail.get('email_type')
    From = mail.get('from')
    To = mail.get('to')
    Subject = mail.get('subject')
    content = mail.get('content')

    if not From:
        From = username

    if isinstance(To, list):  # To 是列表,就用分隔符合并
        To = ','.join(To)

    if not email_type or (email_type not in ("plain", "html")):
        email_type = "html"

    main_msg = MIMEMultipart()  # 构造MIME Multipart 对象做为根容器

    # 添加公共信息
    main_msg['Subject'] = Subject
    main_msg['From'] = From
    main_msg['To'] = To
    # main_msg.preamble = content[:100]       # 序文

    # 构造MIMEText对象做为邮件显示内容并附加到根容器,统一使用 utf-8
    text_msg = MIMEText(content, email_type, 'utf-8')
    main_msg.attach(text_msg)

    if images:
        for f in images:
            fp = open(f, 'rb')
            img_msg = MIMEImage(fp.read())  # 没有 _subtype 参数,MIMEImage 会自己探测图片类型
            fp.close()

            # 设置附件头
            basename = os.path.basename(f)
            img_msg.add_header('content-disposition',
                               'image' + str(images.index(f)), filename=basename)
            main_msg.attach(img_msg)

    if attachments:
        # 构造MIMEBase对象做为文件附件内容并附加到根容器
        for f in attachments:
            basename = os.path.basename(f)
            # 判断文件 MIME
            if "." in basename:  # 带扩展名的
                content_type = mimetypes.types_map["." + basename.split(".")[-1]]
            else:  # 无扩展名的
                content_type = 'application/octet-stream'
            maintype, subtype = content_type.split('/', 1)

            fp = open(f, 'rb')
            file_msg = MIMEBase(maintype, subtype)
            file_msg.set_payload(fp.read())
            fp.close()

            encoders.encode_base64(file_msg)

            # 设置附件头
            # file_msg.add_header('Content-Disposition',
            #                     'attachment' + str(images.index(f)), filename=basename)
            file_msg.add_header('Content-Disposition',
                                'attachment', filename=basename)

            main_msg.attach(file_msg)

    smtp = smtplib.SMTP(smtpserver)

    if use_ssl:  # 使用 ssl 的情况
        smtp.ehlo()
        smtp.starttls()
        smtp.ehlo()
    smtp.login(username, password)
    # smtp.set_debuglevel(1)            # 调试模式
    smtp.sendmail(From, To, main_msg.as_string())
    smtp.quit()

    return True
