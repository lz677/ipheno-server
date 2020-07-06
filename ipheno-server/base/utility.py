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


def is_ipv4(ip: str) -> bool:
    """
    检查ip是否合法
    :param: ip ip地址
    :return: True 合法 False 不合法
    """
    return True if [1] * 4 == [x.strip().isdigit() and 0 <= int(x.strip()) <= 255 for x in ip.split(".")] else False


def is_port(port: str, protocol: str = 'http') -> bool:
    """
    检测port是否是合法的协议代理服务器常用端口号
    :param protocol: http ftp socks Telnet
    :param port: 端口号
    :return: True 端口号是'80', '8080', '3128', '8081', '9098'中一个 False 不可用
    """
    port = port.strip()
    if protocol.lower() == 'http':
        return True if port.isdigit() and port in ('80', '8080', '3128', '8081', '9098') else False
    elif protocol.lower() == 'ftp':
        return True if port.isdigit() and port in ('21',) else False
    elif protocol.lower() == 'socks':
        return True if port.isdigit() and port in ('1080',) else False
    elif protocol.lower() == 'telnet':
        return True if port.isdigit() and port in ('23',) else False
    else:
        return False


def is_img(name: str) -> bool:
    if name.lower().endswith(('.bmp', '.dib', '.png', '.jpg', '.jpeg', '.pbm', '.pgm', '.ppm', '.tif', '.tiff')):
        return True
    return False
