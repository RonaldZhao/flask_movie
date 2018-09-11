# Flask 构建微电影视频网站

学习慕课网课程 [Python Flask 构建微电影视频网站](https://coding.imooc.com/class/124.html) 的代码.

## 开发环境

1. OS: windows10 pro

2. Python: 3.6.6

3. 虚拟化环境: virtualenv

4. 代码编辑器: Atom

## 创建虚拟化环境

> 注意: 在进行此步骤之前请确保`python`已安装.

首先安装`virtualenv`: `pip install virtualenv`.

然后`cd`到你要把虚拟环境保存的目录, 然后执行`virtualenv movie --no-site-packages`.

最后执行`.\movie\Scripts\activate`激活虚拟环境.(如果是PowerShell的话请参考[Windows PowerShell 无法激活 python 虚拟环境问题的解决](https://ronaldzhao.top/devtools/powershell.html))

> 退出虚拟环境命令: `.\movie\Scripts\deactivate.bat`

## 安装 Flask

请先执行`pip freeze`确保没有输出, 即环境干净, 如果有输出请检查是否是在创建虚拟环境的时候没有使用`--no-site-packages`参数.(虚拟环境的删除只要把该目录删除即可)

然后执行`pip install flask`安装 Flask.

安装完毕后再次执行`pip freeze`可以看到:

```bash
(movie) λ pip freeze
click==6.7
Flask==1.0.2
itsdangerous==0.24
Jinja2==2.10
MarkupSafe==1.0
Werkzeug==0.14.1
(movie) λ
```

## 前后台项目目录结构

```bash
project_name
    ├─manage.py                 # 入口启动脚本
    └─app                       # 项目APP
        ├─__init__.py           # 初始化文件
        ├─models.py             # 数据模型文件
        ├─admin                 # 后台模块
        |    ├─__init__.py      # 初始化脚本
        |    ├─views.py         # 视图处理文件
        |    └─forms.py         # 表单处理文件
        ├─home                  # 前台模块
        |    ├─__init__.py      # 初始化脚本
        |    ├─views.py         # 视图处理文件
        |    └─forms.py         # 表单处理文件
        ├─static                # 静态目录
        └─templates             # 模板文件
            ├─admin             # 后台模板
            └─home              # 前台模板
```

## 蓝图构建项目目录

### 什么是蓝图?

一个应用或跨应用中制作应用组件和支持通用的模式.

### 蓝图的作用?

- 将不同的功能模块化

- 构建大型应用

- 优化项目结构

- 增强可读性, 易于维护

## 会员及会员登录日志数据模型设计

1. 首先安装数据库连接依赖包: `pip install flask-sqlalchemy`

2. 然后安装`MySQL`数据库驱动: `pip install PyMySQL`

3. 定义MySQL数据库连接

```python
from flask_sqlalchemy import SQLAlchemy
from flask import Flask

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql://root:root@localhost/movie'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = True
db = SQLAlchemy(app)
```

## 前台布局搭建

1. 静态文件引入: `{{ url_for('static', filename='文件路径') }}`

2. 定义路由: {{ url_for('模块名.视图名', 变量=参数) }}

3. 定义数据块: {% block 数据块名称 %}...{% endblock %}

## 用户登录页面搭建

### 登录

```python
@home.route('/login/')
def login():
    return render_template('home/login.html')

```

### 退出

```python
@home.route('/logout/')
def logout():
    return redirect(url_for('home.login'))

```

## 用户注册页面搭建

```python
@home.route('/register/')
def register():
    return render_template('home/register.html')

```

## 用户个人中心页面搭建

- 用户个人中心: `@home.route('/user/')`
- 修改密码: `@home.route('/pwd/')`
- 评论记录: `@home.route('/comments/')`
- 登录日志: `@home.route('/loginlog/')`
- 收藏电影: `@home.route('/moviecol/')`

## 电影列表页面搭建

### 列表

```python
@home.route('/')
def inddex():
    return render_template('home/index.html')

```

### 动画

```python
@home.route('/animation/')
def animation():
    return render_template('home/animation.html')

```

## 电影搜索页面搭建

```python
@home.route('/search/')
def search():
    return render_template('home/search.html')

```

## 电影详情页面搭建

```python
@home.route('/play/')
def play():
    return render_template('home/play.html')

```

## 404页面搭建

```python
@app.errorhandler(404)
def page_not_found():
    return render_template('common/404.html'), 404

```

## 管理员登录页面搭建

```python
# 登录
@admin.route('/login/')
def login():
    return render_template('admin/login.html')


# 退出
@admin.route('/logout/')
def logout():
    return render_template('admin/logout.html')

```

## 后台布局页面搭建

```python
# admin.html
{% block css %}{% endblock %}
{% include 'grid.html' %}
{% block content %}{% endblock %}
{% block js %}{% endblock %}

# 其他页面继承父模板
{% extends 'admin/admin.html' %}
{% block css %}{% endblock %}
{% include 'grid.html' %}
{% block content %}{% endblock %}
{% block js %}{% endblock %}
```

## 控制面板页面搭建

```python
@admin.route('/')
def index():
    return render_template('admin/index.html')

```

## 标签管理页面搭建

```python
# 添加标签
@admin.route('/tag/add/')
def tag_add():
    return render_template('admin/tag_add.html')


# 标签列表
@admin.route('/tag/list/')
def tag_list():
    return render_template('admin/tag_list.html')

```

## 电影管理页面搭建

```python
# 添加电影
@admin.route('/movie/add/')
def movie_add():
    return render_template('admin/movie_add.html')


# 电影列表
@admin.route('/movie/list/')
def movie_list():
    return render_template('admin/movie_list.html')

```

## 上映预告管理页面搭建

```python
# 添加上映预告
@admin.route('/preview/add/')
def preview_add():
    return render_template('admin/preview_add.html')


# 上映预告列表
@admin.route('/preview/list/')
def preview_list():
    return render_template('admin/preview_list.html')

```

## 用户管理页面搭建

```python
# 用户列表
@admin.route('/user/list/')
def user_list():
    return render_template('admin/user_list.html')


# 查看用户
@admin.route('/user/view/')
def user_view():
    return render_template('admin/user_view.html')

```

## 评论管理页面搭建

```python
# 评论列表
@admin.route('/comment/list/')
def comment_list():
    return render_template('admin/comment_list.html')

```

## 收藏管理页面搭建

```python
# 收藏列表
@admin.route('/moviecol/list/')
def moviecol_list():
    return render_template('admin/moviecol_list.html')

```

## 操作日志管理页面搭建

```python
# 操作日志列表
@admin.route('/oplog/list')
def oplog_list():
    return render_template('admin/oplog_list.html')

```

## 管理员日志管理页面搭建

```python
# 管理员日志列表
@admin.route('/adminloginlog/list')
def adminloginlog_list():
    return render_template('admin/adminloginlog_list.html')

```

## 用户日志管理页面搭建

```python
# 用户日志列表
@admin.route('/userloginlog/list')
def userloginlog_list():
    return render_template('admin/userloginlog_list.html')

```

## 角色管理页面搭建

```python
# 添加角色
@admin.route('/role/add/')
def role_add():
    return render_template('admin/role_add.html')


# 角色列表
@admin.route('/role/list/')
def role_list():
    return render_template('admin/role_list.html')

```

## 权限管理页面搭建

```python
# 添加权限
@admin.route('/auth/add/')
def auth_add():
    return render_template('admin/auth_add.html')


# 权限列表
@admin.route('/auth/list/')
def auth_list():
    return render_template('admin/auth_list.html')
```

## 管理员管理页面搭建

```python
# 添加管理员
@admin.route('/admin/add/')
def admin_add():
    return render_template('admin/admin_add.html')


# 管理员列表
@admin.route('/admin/list/')
def admin_list():
    return render_template('admin/admin_list.html')

```

## 管理员登录

1. 在`app/__init__.py`中创建`db`对象;
2. 在`app/models.py`中导入`db`对象;
3. 在`app/admin/forms.py`中定义表单验证;
4. 在`app/templates/admin/login.html`中使用表单字段, 验证信息和消息闪现;
5. 在`app/admin/views.py`中处理登录请求, 保存会话;
6. 在`app/admin/views.py`中定义登录装饰器和访问控制.
