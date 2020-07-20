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

from flask import Flask, render_template, Response, request, send_file, redirect
from flask.json import jsonify
from base import Hardware
from base import Results
from base import utility

app = Flask(__name__)
hardware_info = Hardware()
results = Results()


# drawer = MotorAction('托盘', [31, 33, 35, 37], [12, 16, 18, 22])
# lifting = MotorAction('抬升', [32, 36, 38, 40], [13, 15, 7, 11])

# web端主页面
@app.route('/')
def main_page():
    return render_template('index.html')


# 硬件状态
@app.route('/status-all')
def status_all():
    # print('status_all')
    return jsonify(hardware_info.get_all_status())


# 总控状态
@app.route('/system/<string:cmd>')
def system(cmd):
    """
    :param cmd: 执行的操作[查看总控信息，设置静态IP，重启总控]
    :return:
    """
    if cmd == "info":
        return jsonify(hardware_info.get_system_info())
    elif cmd == "set-staticIP":
        if request.method == "GET":
            ip = request.args.get("staticIp")
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
                time.sleep(3)
                hardware_info.system_info["staticIP"]["ip"] = request.args.get("staticIp")
                hardware_info.system_info["staticIP"]["port"] = request.args.get("port")
                return jsonify({"state": "ok"})
            else:
                return jsonify({"state": "default"})

    elif cmd == "restart":
        # if hardware_info.all_status['main'] == "运行中":
        # TODO：树莓派重新启动
        print("系统正在重启，10s后重启完毕")
        time.sleep(10)
        # sudo shutdown -r now    sudo reboot


# 相机
# 打开
@app.route('/open-camera')
def open_camera():
    print('打开相机')
    if not hardware_info.capture.isOpened():
        hardware_info.capture.open()
    hardware_info.capture.start_stream()
    return (jsonify({'state': "ok"}) if hardware_info.capture.isOpened()
            else jsonify({'state': "failed"}))  # ok, failed


# 关闭
@app.route('/close-camera')
def close_camera():
    print("关闭相机")
    hardware_info.capture.stop_stream()
    # hardware_info.capture.release()  # cv2的release()有bug
    # 直接返回ok即可
    return jsonify({'state': "ok"})


# 实时图像 b''
@app.route('/realtime-img')
def realtime_img():
    return Response(hardware_info.capture.gen_stream(), mimetype='multipart/x-mixed-replace; boundary=frame')


# 托盘
@app.route('/plate/<string:cmd>')
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
@app.route('/lift/<string:cmd>')
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
@app.route('/weight/<string:cmd>')
def weight(cmd):
    if cmd == "zero":
        print("正在清零（去皮）...2s")
        time.sleep(2)
        hardware_info.all_status['balance'] = 0.00
        # TODO：测量结果为0.00 用测量值替换 hardware_info.all_status['balance']
        return jsonify({"state": "ok"}) if hardware_info.all_status['balance'] == 0.00 else jsonify({"state": "failed"})
    elif cmd == "weight":
        print("正在称重... 2s")
        time.sleep(2)
        hardware_info.all_status['balance'] = 6.77
        return jsonify({"state": "ok"}) if hardware_info.all_status['balance'] == 6.77 else jsonify({"state": "failed"})
    else:
        print("检查你的url")
        return jsonify({"error": "404 [check you url]"})


# 照明
@app.route('/light/<string:cmd>')
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
@app.route('/light_plate/<string:cmd>')
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
@app.route('/fan/<string:cmd>')
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


# 暂时不测试
@app.route('/results', methods=["GET", "POST"])
def results():
    if request.method == "GET":
        return render_template("staticimage.html")

    if request.method == "POST":
        if request.args.get("remote") == '1':
            # TODO base64还是file格式有待确定
            image = request.files.get("image")
            # 两种方式 1. 远程的图片 接收图片和名称  2. 总控传递过去的图片 只接受名称（核对方式）
            if utility.is_img(image.filename):
                # path = ''
                image.save('./static/' + image.filename)
                # TODO 调用算法 算法直接读取存储图片
                print("正在调用算法计算... 5s")
                time.sleep(5)
                # 返回结果
                results.img_info["imageName"] = image.filename
                results.img_info["image"] = './static/' + image.filename
                cal_results = results.get_image_parameters()
                # 算法返回的图片 以 base64 的方式 存储在 imageBase64的属性里。
                cal_results.update(results.get_image_info())
                return jsonify(cal_results)
            else:
                return jsonify({'state': 'check your file'})
        elif request.args.get("imageName") is not None:
            # TODO 调用算法 传递给算法参数
            print("正在调用算法计算... 5s")
            time.sleep(5)
            # 返回结果
            results.img_info["imageName"] = request.args.get("imageName")
            cal_results = results.get_image_parameters()
            # 算法返回的图片 以 base64 的方式 存储在 imageBase64的属性里。
            cal_results.update(results.get_image_info())
            return jsonify(cal_results)
        else:
            print("检查你的url")
            return jsonify({"error": "404 [check you url]"})


# 故障信息
@app.route('/hardware-problem')
def hardware_problem():
    print("正在返回故障信息.... 2s")
    time.sleep(2)
    return jsonify(hardware_info.get_error_info())
