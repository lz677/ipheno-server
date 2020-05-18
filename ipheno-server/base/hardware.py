#!/usr/bin/env python
# encoding: utf-8

"""
@version: Python3.7
@author: Zhiyu YANG  Liu Zhe
@e-mail: zhiyu_yang@sjtu.edu.cn  LiuZhe_54677@sjtu.edu.cn
@file: hardware.py
@time: 2020/5/5 14:49

Code is far away from bugs with the god animal protecting
"""
from base import Capture, __VERSION__


class Hardware:
    def __init__(self):
        self.all_status = {
            'camera': '未连接',
            'balance': '10000',
            'printer': '未连接',
            'light': False,
            'fan': False,
            'plate': '弹出',
            'main': '运行中'
        }
        self.system_info = {
            'version': __VERSION__,
            'staticIP': {
                'ip': '192.168.1.7',
                'port': '8080'
            }
        }
        self.capture = Capture()

    def get_system_info(self):
        return self.system_info.copy()

    def get_all_status(self) -> dict:
        self.all_status['capture'] = '已连接' if self.capture.isOpened() else '未连接'
        return self.all_status.copy()
