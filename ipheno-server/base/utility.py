#!/usr/bin/env python
# encoding: utf-8

"""
@version: Python3.7
@author: Zhiyu YANG
@e-mail: zhiyu_yang@sjtu.edu.cn
@file: utility.py
@time: 2020/5/5 17:12

Code is far away from bugs with the god animal protecting
"""

import pickle


def save_data(filename: str, data):
    with open(filename, 'wb') as f:
        pickle.dump(data, f)


def load_data(filename: str):
    with open(filename, 'rb') as f:
        return pickle.load(f)
