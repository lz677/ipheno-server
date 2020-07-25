#! C:\Users\93715\Anaconda3\python.exe
# *-* coding:utf8 *-*
"""
@author: LiuZhe
@license: (C) Copyright SJTU ME
@contact: LiuZhe_54677@sjtu.edu.cn
@file: app_web.py
@time: 2020/7/20 18:57
@desc: LESS IS MORE
"""

import time
import json
import os
import sys
import logging
import logging.config
import hardware_detect
from flask import Flask, render_template, Response, request, send_file, redirect
from flask.json import jsonify
from blinker import Namespace

# my_signals = Namespace()
# easy_mode_signal = my_signals.signal('easy_mode_signal')

from base import Hardware
from base import Results
from base import utility
from base import easy_mode
from threading import Lock

path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'config\\logging.conf')
# print(path)
# 日志
logging.config.fileConfig(path)
logger = logging.getLogger('iphenoDebug')

app_web = Flask(__name__)
app_web.register_blueprint(easy_mode.easy_mode_app)
hardware_info = Hardware()
results_info = Results()
hardware_det = hardware_detect.HardwareDetect()


# drawer = MotorAction('托盘', [31, 33, 35, 37], [12, 16, 18, 22])
# lifting = MotorAction('抬升', [32, 36, 38, 40], [13, 15, 7, 11])


@app_web.errorhandler(404)
def error404(args):
    return args


# web端主页面
@app_web.route('/')
def main_page():
    logger.info("fangwenle")
    return render_template('index.html')


# 硬件状态
@app_web.route('/status-all/<string:cmd>')
def status_all(cmd='all'):
    # print('status_all')
    if cmd == 'all':
        return jsonify(hardware_info.get_all_status())
    elif cmd in ('camera', 'balance', 'printer', 'light', 'light_plate', 'lifting', 'fan', 'plate', 'main'):
        return jsonify({'state': hardware_info.all_status[cmd]})
    else:
        return jsonify({"error": "404 [check you url]"})


# 总控状态
@app_web.route('/system/<string:cmd>')
def system(cmd):
    """
    :param cmd: 执行的操作[查看总控信息， 设置静态IP， 重启总控]
    :return:
    """
    if cmd == "info":
        return jsonify(hardware_info.get_system_info())
    elif cmd == "set-ip":
        if request.method == "GET":
            ip = request.args.get("ip")
            port = request.args.get("port")
            # ip和port 都合法才可以修改
            if ip is not None or port is not None:
                if not utility.is_ipv4(ip):
                    return jsonify({"state": "invalid_ip"})
                if not utility.is_port(port):
                    return jsonify({"state": "invalid_port"})
                # TODO：树莓派执行静态IP覆盖
                # 硬件操作 用3s 占空
                print("修改ip地址和端口中，等待3s")
                utility.network_setup(ip, '255.255.255.0', '192.168.0.255')
                time.sleep(3)
                hardware_info.system_info["staticIP"]["ip"] = request.args.get("staticIp")
                hardware_info.system_info["staticIP"]["port"] = request.args.get("port")
                if utility.save_info_to_json(hardware_info, './config/main_control.json'):
                    return jsonify({"state": "ok"})
                else:
                    return jsonify({"state": "failed"})
            else:
                return jsonify({"state": "default"})

    elif cmd == "restart":
        # if hardware_info.all_status['main'] == "运行中":
        # TODO：树莓派重新启动
        print("系统正在重启，2s后重启完毕")
        time.sleep(2)
        return jsonify({"state": "ok"})
        # sudo shutdown -r now    sudo reboot


# 相机
@app_web.route('/camera/<string:cmd>')
def camera(cmd):
    if cmd == 'open':
        print('打开相机')
        if not hardware_info.capture.is_opened():
            hardware_info.capture.open()
        hardware_info.capture.start_stream()
        return (jsonify({'state': "ok"}) if hardware_info.capture.is_opened() else jsonify(
            {'state': "failed"}))  # ok, failed
    elif cmd == 'close':
        print("关闭相机")
        hardware_info.capture.stop_stream()
        # hardware_info.capture.release()  # cv2的release()有bug
        # 直接返回ok即可
        return jsonify({'state': "ok"})
    else:
        return jsonify({"error": "404 [check you url]"})


# 实时图像
@app_web.route('/realtime-img')
def realtime_img():
    if not hardware_info.capture.is_opened():
        hardware_info.capture.open()
    hardware_info.capture.start_stream()
    return Response(hardware_info.capture.gen_stream_web(), mimetype='multipart/x-mixed-replace; boundary=frame')


@app_web.route('/realtime-img-app')
def realtime_img_app():
    if not hardware_info.capture.is_opened():
        hardware_info.capture.open()
    hardware_info.capture.start_stream()
    hardware_info.capture.gen_stream_web()
    return redirect('/static/1.jpg')


# 托盘
@app_web.route('/plate/<string:cmd>')
def plate(cmd):
    """
    open or close the plate
    :param cmd: open close
    :return: ok failed 404 [check you url]
    """
    print("plate:", cmd)
    if cmd == "open":
        print("打开托盘... 2s")
        if hardware_info.all_status['lifting']:
            # if drawer.action(False, 8000, 5):
            time.sleep(2)
            hardware_info.all_status['plate'] = False
        return jsonify({'state': "failed"}) if hardware_info.all_status['plate'] else jsonify({'state': "ok"})
    elif cmd == "close":

        if not hardware_info.all_status['lifting']:
            print("关闭托盘... 2s")
            # if drawer.action(True, 8000, 5):
            #     TODO: 托盘不自锁 可能会弹开
            #     drawer.motor.set_able_status(True)
            time.sleep(2)
            hardware_info.all_status['plate'] = True
        return jsonify({'state': "ok"}) if hardware_info.all_status['plate'] else jsonify({'state': "failed"})
    else:
        print("检查你的url")
        return jsonify({"error": "404 [check you url]"})


# 抬升
@app_web.route('/lift/<string:cmd>')
def lift(cmd):
    """
    lift up or down
    :param cmd: up dowm
    :return: ok failed 404 [check you url]
    """
    print("lifting:", cmd)
    if cmd == "up":
        if not hardware_info.all_status['lifting']:
            # if lifting.action(True, 1600, 20):
            print('抬升中.... 2s')
            time.sleep(2)
            hardware_info.all_status['lifting'] = True
        return jsonify({'state': "ok"}) if hardware_info.all_status['lifting'] else jsonify({'state': "failed"})
    elif cmd == "down":
        if hardware_info.all_status['lifting']:
            print('下降中.... 2s')
            time.sleep(2)
            # if lifting.action(False, 1600, 10):
            hardware_info.all_status['lifting'] = False
        return jsonify({'state': "ok"}) if not hardware_info.all_status['lifting'] else jsonify({'state': "failed"})
    else:
        print("检查你的url")
        return jsonify({"error": "404 [check you url]"})


# 称重
@app_web.route('/weight/<string:cmd>')
def weight(cmd):
    if cmd == "zero":
        print("正在清零（去皮）...2s")
        time.sleep(2)
        hardware_info.all_status['balance'] = 0.00
        # TODO：测量结果为0.00 用测量值替换 hardware_info.all_status['balance']
        return jsonify({"state": "ok"}) if hardware_info.all_status['balance'] == 0.00 else jsonify({"state": "failed"})
    elif cmd == "result":
        print("正在称重... 2s")
        time.sleep(2)
        hardware_info.all_status['balance'] = 6.77
        return jsonify({"state": "ok"}) if hardware_info.all_status['balance'] == 6.77 else jsonify({"state": "failed"})
    else:
        print("检查你的url")
        return jsonify({"error": "404 [check you url]"})


# 照明
@app_web.route('/light/<string:cmd>')
def light_handle(cmd):
    """
    open or close the light
    :param cmd: cmd: open close
    :return: ok failed 404 [check you url]
    """
    print("light:", cmd)
    if cmd == "on":
        if not hardware_info.all_status["light"]:
            print("正在开灯... 2s")
            time.sleep(2)
            # TODO：开灯
            hardware_info.all_status["light"] = True
        return jsonify({'state': "ok"}) if hardware_info.all_status["light"] else jsonify({'state': "failed"})
    elif cmd == "off":
        if hardware_info.all_status["light"]:
            print("正在关灯... 2s")
            # TODO：关灯
            time.sleep(2)
            hardware_info.all_status["light"] = False
        return jsonify({'state': "ok"}) if not hardware_info.all_status["light"] else jsonify({'state': "failed"})
    else:
        print("检查你的url")
        return jsonify({"error": "404 [check you url]"})


# 发光板
@app_web.route('/light_plate/<string:cmd>')
def light_plate_handle(cmd):
    """
    open or close the light
    :param cmd: cmd: open close
    :return: ok failed 404 [check you url]
    """
    print("light:", cmd)
    if cmd == "on":
        if not hardware_info.all_status["light_plate"]:
            print("正在开灯... 2s")
            time.sleep(2)
            # TODO：开灯
            hardware_info.all_status["light_plate"] = True
        return jsonify({'state': "ok"}) if hardware_info.all_status["light_plate"] else jsonify({'state': "failed"})
    elif cmd == "off":
        if hardware_info.all_status["light_plate"]:
            print("正在关灯... 2s")
            # TODO：关灯
            time.sleep(2)
            hardware_info.all_status["light_plate"] = False
        return jsonify({'state': "ok"}) if not hardware_info.all_status["light_plate"] else jsonify({'state': "failed"})
    else:
        print("检查你的url")
        return jsonify({"error": "404 [check you url]"})


# 风扇
@app_web.route('/fan/<string:cmd>')
def fan(cmd):
    """
    open or close the fan
    :param cmd: open close
    :return: ok failed 404 [check you url]
    """
    print("fan:", cmd)
    if cmd == "open":
        if not hardware_info.all_status["fan"]:
            print("正在打开风扇... 2s")
            # TODO：开风扇
            time.sleep(2)
            hardware_info.all_status["fan"] = True
        return jsonify({'state': "ok"}) if hardware_info.all_status["fan"] else jsonify({'state': "failed"})
    elif cmd == "close":
        if not hardware_info.all_status["fan"]:
            # TODO：关风扇
            print("正在关闭风扇... 2s")
            time.sleep(2)
            hardware_info.all_status["fan"] = False
        return jsonify({'state': "ok"}) if not hardware_info.all_status["fan"] else jsonify({'state': "failed"})
    else:
        print("检查你的url")
        return jsonify({"error": "404 [check you url]"})


# 打印机
@app_web.route('/printer/<string:cmd>', methods=["GET", "POST"])
def printer(cmd):
    """
    TODO: 待完善
    print the  results
    :return:
    """
    if cmd == "status":
        print("查询打印机状态中")
        time.sleep(2)
        return jsonify({'state': "connected"})
    if cmd == 'print':
        # 查询打印机状态 0 表示正常
        # 正常则打印 异常则返回前端
        print("打印中...... 2s")
        time.sleep(2)
        return jsonify({'state': "ok"})


@app_web.route('/restart')
def restart():
    print("重启代码喽")
    if utility.save_info_to_json(hardware_info, './config/main_control.json'):
        time.sleep(1)
        os.execv(sys.executable, ['python'] + sys.argv)
    else:
        return {'state': 'failed'}


@app_web.route('/reboot')
def reboot():
    print("重启马上")
    if utility.save_info_to_json(hardware_info, './config/main_control.json'):
        time.sleep(1)
        os.system('sudo reboot')
    else:
        return {'state': 'failed'}


# 参数
@app_web.route('/results/<string:cmd>', methods=["GET", "POST"])
def results(cmd):
    if cmd == 'parameters':
        # TODO 调用算法 算法直接读取存储图片
        print("正在调用算法计算... 2s")
        time.sleep(2)
        # 返回结果
        cal_results = results_info.get_image_parameters()
        # 算法返回的图片 以 base64 的方式 存储在 imageBase64的属性里。
        cal_results.update(results_info.get_image_info())
        return jsonify(cal_results)
    else:
        print("检查你的url")
        return jsonify({"error": "404 [check you url]"})


# 故障信息
@app_web.route('/hardware_errors')
def hardware_errors():
    print("正在返回故障信息.... 2s")
    time.sleep(2)
    return jsonify(hardware_info.get_error_info())


# 简易模式
@app_web.route('/easy-mode/<string:cmd>')
def easy_mode(cmd):
    if cmd == 'all':
        # 步骤1 关闭托盘
        print("步骤1：确保托盘关闭... 2s")
        # if drawer.action(True, 8000, 5):
        #     TODO: 托盘不自锁 可能会弹开
        #     drawer.motor.set_able_status(True)
        time.sleep(2)
        # 修改并返回当前状态
        # return jsonify({"state": "close the plate"})

        # 步骤2 称重
        print("步骤2：称重.... 2s")
        # 确保关闭
        # 下降
        # 测量
        # 归位
        # 修改测量数据
        time.sleep(2)
        # 修改并返回当前状态

        # 步骤3
        print("步骤3：图像分析... 2s")
        # 确保电机均处于合适位置
        # 循环 退出（算法返回合适结果）
        #      拍照
        #      调用算法
        #      接受算法返回（照片不合适、灯光不合适）
        # 修改算法结果参数
        time.sleep(2)
        # 修改并返回当前状态
        return jsonify({"state": "ok"})

    if cmd == 'all':
        print("步骤4：弹出托盘... 2s")
        # 确保电机抬升至合适位置
        # 弹出托盘
        time.sleep(2)
        # 修改并返回当前状态
        return jsonify({"state": "ok"})


@app_web.route('/process/<string:cmd>')
def process(cmd):
    if cmd == 'easy-mode':
        return jsonify({'state': ''})


# TODO: 加锁和增加png格式
@app_web.route('/img/<string:image_name>')
def img_realtime(image_name):
    if image_name.endswith(".jpg"):
        if not hardware_info.capture.is_opened():
            hardware_info.capture.open()
        hardware_info.capture.start_stream()
        return Response(hardware_info.capture.gen_stream(), mimetype="image/jpg")
    if image_name == 'static-img':
        if not hardware_info.capture.is_opened():
            hardware_info.capture.open()
        hardware_info.capture.start_stream()
        return Response(hardware_info.capture.gen_stream(False), mimetype="image/png")


# 更新模型
@app_web.route('/update-project')
def update_project():
    utility.update_project('/home/pi/Documents/hh')
    return 'ok'


if __name__ == '__main__':
    print("版本自检 2s")
    time.sleep(2)
    # 开机硬件自检
    print("开机自检")
    hardware_det.like_detect(2)
    time.sleep(2)
    print("读取配置")
    utility.read_info_from_json(hardware_info)
    time.sleep(2)
    print('自检完成')
    print()
    print('*' * 30)
    # 开机算法版本自检
    app_web.run(debug=True, host='0.0.0.0', port=hardware_info.system_info['staticIP']['port'])
