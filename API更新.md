# 07.22

1. 硬件状态允许单个硬件查询

   ```python
   @app_web.route('/status-all/<string:cmd>')
   def status_all(cmd='all'):
       # print('status_all')
       if cmd == 'all':
           return jsonify(hardware_info.get_all_status())
       elif cmd in ('camera', 'balance', 'printer', 'light', 'light_plate', 'lifting', 'fan', 'plate', 'main'):
           return jsonify({'state': hardware_info.all_status[cmd]})
       else:
           return jsonify({"error": "404 [check you url]"})
   ```

   

2. 实时图像路由 将 `_` 改为 `-`

   ```python
   # 实时图像
   @app_web.route('/realtime-img')
   def realtime_img():
       return Response(hardware_info.capture.gen_stream(), mimetype='multipart/x-mixed-replace; boundary=frame')
   ```

3. 增添简易模式路由