#!/usr/bin/env python
# encoding: utf-8

"""
@version: Python3.7
@author: Zhiyu YANG, Liu Zhe
@e-mail: zhiyu_yang@sjtu.edu.cn, LiuZhe_54677@sjtu.edu.cn
@file: capture.py
@time: 2020/5/5 14:40

Code is far away from bugs with the god animal protecting
"""
import cv2
import numpy as np
import time
import base64


class CaptureWebCam:
    def __init__(self):
        super().__init__()
        self.cap = cv2.VideoCapture()
        self.will_quit = False
        self.save_img = False
        self.img_stream = "NONE"
        _, self.blackJpeg = cv2.imencode('.jpg', np.zeros(shape=(480, 720), dtype=np.uint8))

        self.should_stream_stop = False

    def open(self, _id=0):
        self.cap.open(_id)

    def isOpened(self) -> bool:
        return self.cap.isOpened()

    def read(self) -> (bool, np.ndarray):
        return self.cap.read()

    def stop_stream(self):
        self.should_stream_stop = True

    def start_stream(self):
        self.should_stream_stop = False

    def gen_stream(self):
        while not self.will_quit:
            if self.cap.isOpened() and not self.should_stream_stop:
                # print('get stream')
                ret, frame = self.read()
                # if self.save_img:
                cv2.imwrite('./static/1.jpg', frame)

                ret, jpeg = cv2.imencode('.jpg', frame)

                yield (b'--frame\r\n'
                       b'Content-Type: image/jpeg\r\n\r\n' + jpeg.tobytes() + b'\r\n\r\n')
            else:
                time.sleep(0.5)
            # else:
            #     yield (b'--frame\r\n'
            #            b'Content-Type: image/jpeg\r\n\r\n' + self.blackJpeg.tobytes() + b'\r\n\r\n')

    def return_img_stream(self):
        while not self.will_quit:
            if self.cap.isOpened() and not self.should_stream_stop:
                ret, self.img_stream = self.read()
                # print(frame)
                ret, jpeg = cv2.imencode('.jpg', self.img_stream)
                img_stream = base64.b64encode(jpeg)
                img_stream = str(img_stream, 'utf8')
                return img_stream
                # yield (b'--frame\r\n'
                #        b'Content-Type: image/jpeg\r\n\r\n' + jpeg.tobytes() + b'\r\n\r\n')
            else:
                time.sleep(0.5)
        # frame = cv2.imread(img_local_path)
        # ret, jpeg = cv2.imencode('.jpg', frame)
        # # with open(img_local_path, 'rb') as img:
        # #     self.img_stream = img.read()
        # self.img_stream = base64.b64encode(jpeg)
        # self.img_stream = str(self.img_stream, 'utf8')
        # return self.img_stream

    def return_static_img(self):
        if self.img_stream == "NONE":
            return "NONE"
        else:
            ret, jpeg = cv2.imencode('.png', self.img_stream)
            img_stream = base64.b64encode(jpeg)
            img_stream = str(img_stream, 'utf8')
            return img_stream

    def release(self):
        self.will_quit = True
        self.cap.release()


if __name__ == '__main__':
    capture = CaptureWebCam()
