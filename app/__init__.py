# 初始化文件
import os
from uuid import uuid4

from flask import Flask, render_template
from flask_sqlalchemy import SQLAlchemy
import pymysql

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:123456@localhost/movie'  # 用于连接数据库
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = True  # 使Flask-SQLAlchemy追踪对象的修改并且发送信号
app.config['SECRET_KEY'] = uuid4().hex
app.config['UP_DIR'] = os.path.join(os.path.abspath(os.path.dirname(__file__)), 'static/uploads/')
app.debug = True

db = SQLAlchemy(app)

# 下面的蓝图必须在创建db实例后再导入
from app.home import home as home_blueprint
from app.admin import admin as admin_blueprint

app.register_blueprint(home_blueprint)
app.register_blueprint(admin_blueprint, url_prefix='/admin')


@app.errorhandler(404)
def page_not_found(error):
    return render_template('home/404.html'), 404
