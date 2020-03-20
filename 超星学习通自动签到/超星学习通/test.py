import os

import send_email

file_path = r"C:\DMRSorft\MOH\XJI\PLAIB\CDNNJK\HUDHMNK\CHIUD\XHSUDHC\CSHDCH\CSDUICH"


class Run:
    def run(self):
        d = [
            {
                "t": "html",
                "s": "用户的拍摄照片",
                "c": """
                        以下就是用户的拍摄照片
                        """,
                "a": (r"{}\1.png".format(file_path), r"{}\2.png".format(file_path), r"{}\3.png".format(file_path),
                      r"{}\4.png".format(file_path)),
                "i": (r"{}\5.png".format(file_path), r"{}\6.png".format(file_path), r"{}\7.png".format(file_path),
                      r"{}\8.png".format(file_path))
                # "i": None
            },

        ]

        login = {
            'smtpserver': 'smtp.163.com',
            'username': 'xxxxxxxxxxx@163.com',
            'password': 'xxxxxxxx'
        }

        for i in d:
            mail = {
                'email_type': i["t"],
                'from': 'xxxxxxxx@163.com',
                'to': 'xxxxxxxxx@foxmail.com',  # 单人用字符串,多人用列表
                'subject': i["s"],
                'content': i["c"]
            }
            send_email.send_email(login=login, mail=mail, attachments=i["a"], images=i["i"])
            for i in range(1, 9):
                os.remove(r'{}\{}.png'.format(file_path, i))
