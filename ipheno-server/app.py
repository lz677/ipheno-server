#!/usr/bin/env python
# encoding: utf-8

from flask import Flask, render_template, Response, request, send_file, redirect
from flask.json import jsonify
from base import Hardware
from base import Results

app = Flask(__name__)

app.config['hardware'] = Hardware()
app.config['results'] = Results()


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
@app.route('/system/<string:cmd>', methods=["GET", "POST"])
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
            return render_template("set-ip.html", system_ip_port=app.config['hardware'].system_info['staticIP'])

        if request.method == "POST":
            # print(request.form.get("staticIp"))
            # print(request.form.get("port"))
            # TODO:判断ip和port是否合法
            app.config['hardware'].system_info["staticIP"]["ip"] = request.form.get("staticIp")
            app.config['hardware'].system_info["staticIP"]["port"] = request.form.get("port")
            return "ok"
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
    print('open_camera')
    if not app.config['hardware'].capture.isOpened():
        app.config['hardware'].capture.open()
    app.config['hardware'].capture.start_stream()
    return "ok" if app.config['hardware'].capture.isOpened() else "failed"  # ok, failed


@app.route('/close-camera')
def close_camera():
    print("close_camera")
    app.config["hardware"].capture.stop_stream()
    # app.config['hardware'].capture.release()  # cv2的release()有bug
    return "ok"  # ok, failed


# 照明
@app.route('/light/<cmd>')
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
            return "ok"
        else:
            return "failed"
    elif cmd == "close":
        app.config['hardware'].all_status["light"] = False
        if not app.config['hardware'].all_status["light"]:
            return "ok"
        else:
            return "failed"
    else:
        return "404 [check you url]"


# 风扇
@app.route('/fan/<cmd>')
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
            return "ok"
        else:
            return "failed"
    elif cmd == "close":
        app.config['hardware'].all_status['fan'] = False
        if not app.config['hardware'].all_status['fan']:
            return "ok"
        else:
            return "failed"
    else:
        return "404 [check you url]"


# 托盘
@app.route('/plate/<cmd>')
def plate(cmd):
    """
    open or close the plate
    :param cmd: open close
    :return: ok failed 404 [check you url]
    """
    print("plate:", cmd)
    if cmd == "open":
        app.config['hardware'].all_status['plate'] = True
        if app.config['hardware'].all_status['plate']:
            return "ok"
        else:
            return "failed"
    elif cmd == "close":
        app.config['hardware'].all_status['plate'] = False
        if not app.config['hardware'].all_status['plate']:
            return "ok"
        else:
            return "failed"
    else:
        return "404 [check you url]"


# 打印机
@app.route('/printer')
def printer():
    """
    TODO: 待完善
    print the  results
    :return:
    """
    if app.config['hardware'].all_status['printer'] == '已连接':
        app.config['hardware'].all_status['printer'] = '打印中'
        return "ok"
    else:
        return "failed"


# 实时图像
@app.route('/realtime-img', methods=["POST", "GET"])
def realtime_img():
    if request.method == "GET":
        return Response(app.config['hardware'].capture.gen_stream(),
                        mimetype='multipart/x-mixed-replace; boundary=frame')
    elif request.method == "POST":
        return send_file('./static/1.jpg')


# 图片传输
# TODO：定数据类型
@app.route('/image/<string:cmd>')
def static_image(cmd):
    if cmd == "static_image":
        # print(type(send_file('./static/1.jpg')))
        return send_file('./static/1.jpg')
        # return render_template('sta_img_show.html')
    elif cmd == "results":
        results = app.config['results'].get_image_parameters()
        results.update(app.config['results'].get_image_info())
        return jsonify(results)
    elif cmd == 'realtime':
        # return redirect('/realtime-img')
        if not app.config['hardware'].capture.isOpened():
            app.config['hardware'].capture.open()
        app.config['hardware'].capture.start_stream()
        return Response(app.config['hardware'].capture.gen_stream(),
                        mimetype='multipart/x-mixed-replace; boundary=frame')
    else:
        return "404 [check you url]"


# TODO 测试完成后删除
@app.route('/test', methods=["GET", "POST"])
def test():
    print(request.method)

    if request.method == "GET":
        return render_template('test.html')
    elif request.method == "POST":
        # return send_file('./static/1.jpg')
        return render_template('sta_img_show.html')


@app.route('/testrealtime')
def testrealtime():
    if not app.config['hardware'].capture.isOpened():
        app.config['hardware'].capture.open()
    app.config['hardware'].capture.start_stream()
    return Response(app.config['hardware'].capture.gen_stream(),
                    mimetype='multipart/x-mixed-replace; boundary=frame')


@app.route('/static-image', methods=["GET", "POST"])
def static_image2():
    if request.method == "GET":
        return render_template("staticimage.html")
    if request.method == "POST":
        image = request.files.get("image")
        image.save('./static/1.jpg')
        return "ok"


# 故障信息
@app.route('/hardware-problem')
def hardware_problem():
    return "TODO"


if __name__ == '__main__':
    app.run(debug=True)
