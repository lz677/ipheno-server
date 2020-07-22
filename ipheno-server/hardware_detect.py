#! C:\Users\93715\Anaconda3\python.exe
# *-* coding:utf8 *-*
"""
@author: LiuZhe
@license: (C) Copyright SJTU ME
@contact: LiuZhe_54677@sjtu.edu.cn
@file: hardware_detect.py
@time: 2020/7/21 13:48
@desc: LESS IS MORE
"""

import time


# 自检测检测
# 控制元件
# 四个行程开关
# 两个电机 一个编码器
# 两个灯的继电器
# 一个风选机
class HardwareDetect(object):
    def __init__(self):
        pass

    # 行程开关自检
    def detect_travel_switch(self) -> bool:
        pass

    # 电机自检
    def detect_motor_switch(self) -> bool:
        pass

    # 编码器自检
    def detect_motor_encoder(self) -> bool:
        pass

    # 灯自检
    def detect_light(self) -> bool:
        pass

    # 风选机自检
    def fan_detect(self) -> bool:
        pass

    # 假检测模块
    def like_detect(self, n):
        print("自检测中，等待%d s...." % n)
