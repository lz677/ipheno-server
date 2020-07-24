#!/usr/bin/env python
# encoding: utf-8

from flask import Flask, render_template, Response, request, send_file, redirect
from flask.json import jsonify
from base import Hardware
from base import Results
from base import utility
from base import Motor, TravelSwitch, MotorAction

app = Flask(__name__)

app.config['hardware'] = Hardware()
app.config['results'] = Results()

drawer = MotorAction('托盘', [31, 33, 35, 37], [12, 16, 18, 22], 8000)
lifting = MotorAction('抬升', [32, 36, 38, 40], [13, 15, 7, 11], 1600)


# 验证文件大小，通过设置Flask内置的配置变量MAX_CONTENT_LENGTH，可以显示请求报文的最大长度，单位是字节
# 当上传文件的大小超过这个限制后，flask内置的开服务器会中断连接，在生产环境的服务器上会返回413错误响应
# app.config['MAX_CONTENT_LENGTH'] = 1 * 1024 * 1024

@app.errorhandler(404)
def error404(args):
    return args


@app.route('/')
def hello_world():
    return render_template('index.html')


# 硬件状态
@app.route('/status-all')
def status_all():
    # print('status_all')
    return jsonify(app.config['hardware'].get_all_status())


# 总控状态
@app.route('/system/<string:cmd>')
def system(cmd):
    # print(cmd)
    """
    :param cmd: 执行的操作[查看总控信息，设置静态IP，重启总控]
    :return:
    """
    if cmd == "info":
        return jsonify(app.config['hardware'].get_system_info())
    elif cmd == "set-staticIp":
        if request.method == "GET":
            ip = request.args.get("staticIp")
            port = request.args.get("port")
            # ip和port 都合法才可以修改
            if ip is not None or port is not None:
                if not utility.is_ipv4(ip):
                    return jsonify({"state": "invalid_ip"})
                if not utility.is_port(port):
                    return jsonify({"state": "invalid_port"})
                app.config['hardware'].system_info["staticIP"]["ip"] = request.args.get("staticIp")
                app.config['hardware'].system_info["staticIP"]["port"] = request.args.get("port")
            else:
                # return jsonify({"state": "default"})
                # Web测试功能时使用
                pass
            # Web测试功能时使用
            return render_template("set-ip.html", system_ip_port=app.config['hardware'].system_info['staticIP'])

    elif cmd == "restart":
        # 重启总控，接受到GET的请求之后，重启总控，返回总控的状态
        # TODO：接收到重启 则修改主控状态为 ‘重启中’
        #  重启中则返回"restarting"
        # restart the system successfully, then return "ok"
        if app.config['hardware'].all_status["main"] == "运行中":
            app.config['hardware'].all_status["main"] = "重启中"
        elif app.config['hardware'].all_status["main"] == "重启中":
            return "restarting"
    else:
        return "404 [check you url]"


# 相机
@app.route('/open-camera')
def open_camera():
    # print('open_camera')
    if not app.config['hardware'].capture.isOpened():
        app.config['hardware'].capture.open()
    app.config['hardware'].capture.start_stream()
    return 'ok' if app.config['hardware'].capture.isOpened() else 'failed'
    # return (jsonify({'state': "ok"}) if app.config['hardware'].capture.isOpened()
    #         else jsonify({'state': "failed"}))  # ok, failed


@app.route('/close-camera')
def close_camera():
    # print("close_camera")
    app.config["hardware"].capture.stop_stream()
    # app.config['hardware'].capture.release()  # cv2的release()有bug
    return 'ok'
    # 直接返回ok即可
    # return (jsonify({'state': "ok"}) if app.config['hardware'].capture.should_stream_stop
    #         else jsonify({'state': "failed"}))  # ok, failed


# 照明
@app.route('/light/<string:cmd>')
def light(cmd):
    """
    open or close the light
    :param cmd: cmd: open close
    :return: ok failed 404 [check you url]
    """
    print("light:", cmd)
    if cmd == "open":
        app.config['hardware'].all_status["light"] = True
        if app.config['hardware'].all_status["light"]:
            # return 'ok'
            return jsonify({'state': "ok"})
        else:
            # return 'failed'
            return jsonify({'state': "failed"})
    elif cmd == "close":
        app.config['hardware'].all_status["light"] = False
        if not app.config['hardware'].all_status["light"]:
            # return 'ok'
            return jsonify({'state': "ok"})
        else:
            # return 'failed'
            return jsonify({'state': "failed"})
    else:
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
        app.config['hardware'].all_status["fan"] = True
        if app.config['hardware'].all_status["fan"]:
            return jsonify({'state': "ok"})
        else:
            return jsonify({'state': "failed"})
    elif cmd == "close":
        app.config['hardware'].all_status['fan'] = False
        if not app.config['hardware'].all_status['fan']:
            return jsonify({'state': "ok"})
        else:
            return jsonify({'state': "failed"})
    else:
        return jsonify({"error": "404 [check you url]"})


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
        # print(app.config['hardware'].all_status['plate'])
        if drawer.action(False, 10):
            app.config['hardware'].all_status['plate'] = False
        if not app.config['hardware'].all_status['plate']:
            # return 'ok'
            return jsonify({'state': "ok"})
        else:
            # return 'failed'
            return jsonify({'state': "failed"})
    elif cmd == "close":
        if drawer.action(True, 10):
            # TODO:托盘不自锁 可能会弹开
            # drawer.motor.set_able_status(True)
            app.config['hardware'].all_status['plate'] = True
        if app.config['hardware'].all_status['plate']:
            # return 'ok'
            return jsonify({'state': "ok"})
        else:
            # return 'failed'
            return jsonify({'state': "failed"})
    else:
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
        # if not app.config['hardware'].all_status['lifting']:
        if lifting.action(True, 20):
            app.config['hardware'].all_status['lifting'] = True
        if app.config['hardware'].all_status['lifting']:
            # return 'ok'
            return jsonify({'state': "ok"})
        else:
            # return 'failed'
            return jsonify({'state': "failed"})
    elif cmd == "down":
        # if app.config['hardware'].all_status['lifting']:
        if lifting.action(False, 10):
            app.config['hardware'].all_status['lifting'] = False
        if not app.config['hardware'].all_status['lifting']:
            # return 'ok'
            return jsonify({'state': "ok"})
        else:
            # return 'failed'
            return jsonify({'state': "failed"})
    else:
        return jsonify({"error": "404 [check you url]"})


# 打印机
@app.route('/printer/<string:cmd>', methods=["GET", "POST"])
def printer(cmd):
    """
    TODO: 待完善
    print the  results
    :return:
    """
    if cmd == "connect":
        app.config['hardware'].all_status['printer'] = '已连接'
        if app.config['hardware'].all_status['printer'] in ('已连接', '打印中'):
            return jsonify({"state": 'connected'})
        elif app.config['hardware'].all_status['printer'] == '未连接':
            return jsonify({"state": 'disconnected'})
        else:
            return jsonify({"error": "error"})

    if cmd == 'print':
        if app.config['hardware'].all_status['printer'] == '已连接':
            app.config['hardware'].all_status['printer'] = '打印中'
            if app.config['hardware'].all_status['printer'] == '打印中':
                return jsonify({"state": 'printing'})
        else:
            return jsonify({"error": "error"})


# 实时图像 base64
@app.route('/realtime-image')
def realtime_image():
    if not app.config['hardware'].capture.isOpened():
        app.config['hardware'].capture.open()
    app.config['hardware'].capture.start_stream()
    # # img_path = './static/1.jpg'
    img_stream = app.config['hardware'].capture.return_img_stream()
    length = len(img_stream)
    # print(img_stream)
    # return Response(app.config['hardware'].capture.return_img_stream())
    return render_template('testbase64.html', img_stream=img_stream, len=length)


# 实时图像 b''
@app.route('/realtime-img')
def realtime_img():
    return Response(app.config['hardware'].capture.gen_stream_web(),
                    mimetype='multipart/x-mixed-replace; boundary=frame')


# 图片传输
# TODO：定数据类型
@app.route('/image/<string:cmd>')
def static_image(cmd):
    if cmd == "static_image":
        # print(type(send_file('./static/1.jpg')))
        img_stream = app.config['hardware'].capture.return_static_img()
        length = len(img_stream)
        return render_template('testbase64.html', img_static=img_stream, len=length)
        # return render_template('sta_img_show.html')
    elif cmd == "results":
        results = app.config['results'].get_image_parameters()
        # 算法返回的图片 以 base64 的方式 存储在 imageBase64的属性里。
        results.update(app.config['results'].get_image_info())
        return jsonify(results)
    else:
        return "404 [check you url]"


# # TODO 测试完成后删除
# @app.route('/test', methods=["GET", "POST"])
# def test():
#     print(request.method)
#
#     if request.method == "GET":
#         return render_template('test.html')
#     elif request.method == "POST":
#         return send_file('./static/1.jpg')
#         # return render_template('sta_img_show.html')
#
#
# @app.route('/testrealtime')
# def testrealtime():
#     if not app.config['hardware'].capture.isOpened():
#         app.config['hardware'].capture.open()
#     app.config['hardware'].capture.start_stream()
#     return Response(app.config['hardware'].capture.gen_stream(),
#                     mimetype='multipart/x-mixed-replace; boundary=frame')


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

                # 返回结果
                app.config['results'].img_info["imageName"] = image.filename
                app.config['results'].img_info["image"] = './static/' + image.filename
                cal_results = app.config['results'].get_image_parameters()
                # 算法返回的图片 以 base64 的方式 存储在 imageBase64的属性里。
                cal_results.update(app.config['results'].get_image_info())
                return jsonify(cal_results)
            else:
                return jsonify({'state': 'check your file'})
        elif request.args.get("imageName") is not None:
            # TODO 调用算法 传递给算法参数
            # 返回结果
            app.config['results'].img_info["imageName"] = request.args.get("imageName")
            cal_results = app.config['results'].get_image_parameters()
            # 算法返回的图片 以 base64 的方式 存储在 imageBase64的属性里。
            cal_results.update(app.config['results'].get_image_info())
            return jsonify(cal_results)
        else:
            return jsonify({"error": "404 [check you url]"})


# 故障信息
@app.route('/hardware-problem')
def hardware_problem():
    return jsonify(app.config['hardware'].get_error_info())


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
