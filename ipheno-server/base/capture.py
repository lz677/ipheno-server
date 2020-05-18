#!/usr/bin/env python
# encoding: utf-8

"""
@version: Python3.7
@author: Zhiyu YANG
@e-mail: zhiyu_yang@sjtu.edu.cn
@file: capture.py
@time: 2020/5/5 14:40

Code is far away from bugs with the god animal protecting
"""
import cv2
import numpy as np
import time


class CaptureWebCam:
    def __init__(self):
        super().__init__()
        self.cap = cv2.VideoCapture()
        self.will_quit = False
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
                ret, jpeg = cv2.imencode('.jpg', frame)
                yield (b'--frame\r\n'
                       b'Content-Type: image/jpeg\r\n\r\n' + jpeg.tobytes() + b'\r\n\r\n')
            else:
                time.sleep(0.5)
            # else:
            #     yield (b'--frame\r\n'
            #            b'Content-Type: image/jpeg\r\n\r\n' + self.blackJpeg.tobytes() + b'\r\n\r\n')

    def release(self):
        self.will_quit = True
        self.cap.release()


if __name__ == '__main__':
    capture = CaptureWebCam()
