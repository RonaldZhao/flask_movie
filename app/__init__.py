# 初始化文件
from flask import Flask
from flask_sqlalchemy import SQLAlchemy

from app.home import home as home_blueprint
from app.admin import admin as admin_blueprint

app = Flask(__name__)
app.debug = True
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql://root:123456@localhost/movie'  # 用于连接数据库
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = True  # 使Flask-SQLAlchemy追踪对象的修改并且发送信号

db = SQLAlchemy(app)

app.register_blueprint(home_blueprint)
app.register_blueprint(admin_blueprint, url_prefix='/admin')
