#!/usr/bin/env python
# encoding: utf-8

"""
@version: Python3.7
@author: Zhiyu YANG
@e-mail: zhiyu_yang@sjtu.edu.cn
@file: __init__.py.py
@time: 2020/5/5 14:40

Code is far away from bugs with the god animal protecting
"""
__VERSION__ = '0.0.1'
from .utility import load_data, save_data
from .capture import CaptureWebCam as Capture
from .hardware import Hardware
from .results import Results

__all__ = ['Capture', 'Hardware', '__VERSION__', 'load_data', 'save_data']
