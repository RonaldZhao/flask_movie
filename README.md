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
