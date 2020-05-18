#!/usr/bin/env python
# encoding: utf-8

from flask import Flask, render_template, Response, request
from flask.json import jsonify
from base import Hardware
app = Flask(__name__)

app.config['hardware'] = Hardware()


@app.route('/')
def hello_world():
    return render_template('index.html')


@app.route('/status-all')
def status_all():
    print('status_all')
    return jsonify(app.config['hardware'].get_all_status())


@app.route('/system-info')
def system_info():
    return jsonify(app.config['hardware'].get_system_info())


# 重启总控，接受到GET的请求之后，重启总控，返回总控的状态
# 重启中 运行中
@app.route('/system-restart')
def system_restart():
    return "ok "


@app.route('/system/<string:cmd>')
def system(cmd):
    print(cmd)
    if cmd == 'info':
        return jsonify(app.config['hardware'].get_system_info())
    elif cmd == 'set-staticIp':
        print(request.url)
        return "setIPing"
        # 设置静态IP
        # app.config['hardware'].system_info['staticIP']['ip'] = "192.168.1.7"
        # app.config['hardware'].system_info['staticIP']['port'] = "8080"


@app.route('/realtime-img')
def realtime_img():
    return Response(app.config['hardware'].capture.gen_stream(),
                    mimetype='multipart/x-mixed-replace; boundary=frame')


@app.route('/fan/<cmd>')
def fan(cmd):
    print('fan:', cmd)
    if cmd == 'open':
        app.config['hardware'].all_status['fan'] = True
        return 'ok'
    elif cmd == 'close':
        app.config['hardware'].all_status['fan'] = False
        return 'ok'


@app.route('/light/<cmd>')
def light(cmd):
    print('light:', cmd)
    if cmd == 'open':
        app.config['hardware'].all_status['light'] = True
        return 'ok'
    elif cmd == 'close':
        app.config['hardware'].all_status['light'] = False
        return 'ok'


@app.route('/open-camera')
def open_camera():
    print('open_camera')
    if not app.config['hardware'].capture.isOpened():
        app.config['hardware'].capture.open()
    app.config['hardware'].capture.start_stream()
    return 'ok' if app.config['hardware'].capture.isOpened() else 'failed'  # ok, failed


@app.route('/close-camera')
def close_camera():
    print('close_camera')
    app.config['hardware'].capture.stop_stream()
    # app.config['hardware'].capture.release()  # cv2的release()有bug
    return 'ok'  # ok, failed


if __name__ == '__main__':
    app.run(debug=True)
