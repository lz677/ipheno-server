[toc]

# Day1

## 三剑客

1. HTTPResponse `return "hello"`

2. render

   ```python
   from flask improt render_tamplate
   return render_tamplate("模板")
   ```

3. redirect

   ```python
   from flask import redirect
   return redirect("/url")
   ```

## 小儿子

1. jsonify #返回json格式，在响应头上加入 Content-Type: application/json

   ```python
   from flask import jsonify
   return jsonify({"k":"v"})
   ```

2. send_file # 打开文件并返回文件内容　自动识别文件类型

## request

```python
request.form # 存储FormData表单中的数据 to_dict()
request.args # 存放URL中的数据 to_dict()
request.json # 在请求头:Content-Type:application/json 自动序列化json
request.data # 在请求头: Content-Type中无法被识别，请求体中数据存在data中 b""
request.methond # 请求方式
request.files # 文件储存　save(file.name)
```

## Session

```python
from flask import session
app.secret_key = "54677"

# ｛user:123｝ + secret_key - respose-cookie 拿到cookie 中存放
# 请求带上cookie - flask收到cookie 中的session 通过secret_key　反序列化
session["user"] = "123"
存在浏览器的cookie中　- 由secret_key + session 加密后存放

```



# Day2

##　装饰器

- 主要问题：装饰器函数名重复
- 解决：
  - `endpoint` 默认视图函数名字
  - `@functools.wraps(装饰函数)`

## flask中的路由

1. `endpoint`  反向生成url地址标志，默认视图函数名 `from flask import url_for`

   ```python
   @app.route("/",endpoint="index")
   ```

2. `methond` 视图函数允许的请求方式

   ```python 
   @app.route("/",methond=["GET","POST"])
   ```

3. `"/index/<string:page>"`动态路由路由参数

   - 注意接收参数`def index(page)`

   ```python
   @app.route("/index/<int:page>",methond=["GET","POST"])
   def index(page)
   	print(page)
       return "123"
   ```

4. 默认参数

   ```python
   @app.route("/",defaults={"nid":"123456"})
   	def index(nid)
   ```

   

5. `strict_slashes `是否严格遵循地址

   ```python
   @app.route("/index",strict_slashes=True)
   False:/index/ True:/index
   ```

6. 永久重定向`redirect_to`,省去过程

   - 应用:如果地址变更了，别人已经收藏了，所以我决定讲原来的地址直接永久重定向。

   ```python
   @app.route("/",redirect_to="/login")
   ```

7. run()

   ```python
   app.run("0.0.0.0",5000,debug = True)
   ```

   

## Flask实例化配置

```python
app = Flask(__name__, template_folder = "temp", static_folder = "statics", static_url_path="/static")
```

- 静态目录访问路径，静态目录：当我访问静态目录访问路径的时候，我就去我制定的静态目录中找。如果只制定静态目录，则静态目录访问地址随之改变。

1. `template_folder = "temp"` 默认模板路径`templates`
2. `static_folder = "statics"`默认静态文件路径 `static`
3. `static_url_path="/static` 默认静态文件路由地址 "/"+`static_folder`

## Flask对象配置

对象配置就是`app.`或者`app.config`

```python
app.config["SECRET_KEY"] = "123456"
app.config["DEBUG"] = True
```

DEBUG模式和TESTING模式

## 蓝图

- 作用:实现功能的插拔随意，把某一整块的功能可以封装到一个蓝图里。

  ```python
  Blueprint # 当成一个不能被启动的app flask实例
  # 使用
  from flask import Blueprint
  s4app = Blueprint("s4app", __name__, template_folder="apptem", url_prefix="/blue")
  
  app.register_blueprint(view.s4app)
  @s4app.route("/s4app")
  ```

- `url_prefix="/blue"` url前缀

  

## 特殊装饰器

- @app.before_request  # 请求进入试图函数之前
  - 应用思路：当没有session的时候，我们需要所有的试图函数都要先进入登录页面来证明自己的身份。一旦有了session，我们跳过登录页面。**但是我们不能在登录也面前加跳转登录的链接，否则会重定向次数过多，所以return None**

```python
@app.before_request  # 请求进入试图函数之前　每个试图函数前都要走一遍
# 注意：返回NONE说明跳过　before_request　内的函数
# 不返回　默认返回ＮＯＮＥ
def be():
    print("i'm before")
    if request.path == '/login':
        return None　　　　　　　
    if not session.get("user"):
        return redirect("/login")
```

- @app.after_request  # 在相应客户端之前

  - 响应客户端之前，进入的参数是response，应该把respose给客户端。

  ```python
  @app.after_request  # 在相应客户端之前
  def af(args):
      print("i'm af")
  ```

- djongo中间键

  

- 返回情况：

  - before **自上而下**
  - after **自下而上**
  - 不是一体的，无论before从哪里断开，都从最下的after依次开始返回
    - 正常的: be1 - be2 - be3 - af3 - af2 - af1
    - 异常情况: be1 - af3 - af2 - af1

- @app.errorhandler(404) # 重定义错误页面返回信息

  ```python
  @app.errorhandler(404)
  def error404(args):
      return 三剑客+小儿子
  ```

## 作业

- 使用蓝图实现　增删改查　4个蓝图

  找字典：四个页面对字典进行增删该查

# Day3

1. CBV - Flsak基础
2. Flask-Session
3. WTForms
4. 数据库连接池

## CBV

```python

```

