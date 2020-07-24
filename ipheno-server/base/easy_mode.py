#! C:\Users\93715\Anaconda3\python.exe
# *-* coding:utf8 *-*
"""
@author: LiuZhe
@license: (C) Copyright SJTU ME
@contact: LiuZhe_54677@sjtu.edu.cn
@file: easy_mode.py
@time: 2020/7/23 10:57
@desc: LESS IS MORE
"""
from flask import Blueprint


easy_mode_app = Blueprint("easy", __name__)


@easy_mode_app.route('/easy')
def step1():
    print("第一步")
    return 'step1'
