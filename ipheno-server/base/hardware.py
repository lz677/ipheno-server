#!/usr/bin/env python
# encoding: utf-8

"""
@version: Python3.7
@author: Zhiyu YANG, Liu Zhe
@e-mail: zhiyu_yang@sjtu.edu.cn, LiuZhe_54677@sjtu.edu.cn
@file: hardware.py
@time: 2020/5/5 14:49

Code is far away from bugs with the god animal protecting
"""
from base import Capture, __VERSION__


class Hardware:
    def __init__(self):
        """
        TODO：目前中间状态交给前端
        The status of hardware
        camera : '未连接' '已连接' '故障'
        balance: '未连接' '重量'
        printer: '未连接' '已连接' '打印中'
        light :   True  False'故障'
        fan :     True  False '故障'
        plate:    True  False
        main：     '运行中'
        """
        # initial status of hardware for reset
        self.init_status = {
            'camera': '未连接',
            'balance': '0',
            'printer': '未连接',
            'light_plate': False,
            'light': False,
            # 'fan': False,
            'plate': False,
            'lifting': False,
            'main': '运行中'
        }

        # hardware status
        self.all_status = {

            'camera': '未连接',
            'balance': '10000',
            'printer': '未连接',
            'light': False,
            'light_plate': False,
            'fan': False,
            'plate': False,
            # 'plate': '关闭',
            'lifting': False,
            'main': '运行中'
        }

        # system information RPi
        self.system_info = {
            'version': __VERSION__,
            'staticIP': {
                'ip': '192.168.1.7',
                'port': '8080'
            }
        }

        # error
        self.error_info = {
            'camera': '正常',  # 相机
            'balance': '正常',  # 秤
            'printer': '正常',  # 打印机
            'light': '正常',  # 灯
            'height': '正常',  # 抬升
            'fan': '正常',  # 风扇
            'plate': '正常',  # 托盘
            'main': '正常'  # 主控
        }

        self.capture = Capture()

    def get_system_info(self):
        return self.system_info.copy()

    def get_all_status(self) -> dict:
        self.all_status['capture'] = '已连接' if self.capture.isOpened() else '未连接'
        return self.all_status.copy()

    def get_init_status(self) -> dict:
        self.init_status['capture'] = '已连接' if self.capture.isOpened() else '未连接'
        return self.init_status.copy()

    def get_error_info(self):
        return self.error_info.copy()
