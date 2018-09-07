# 初始化文件
from flask import Flask

from app.home import home as home_blueprint
from app.admin import admin as admin_blueprint

app = Flask(__name__)
app.debug = True

app.register_blueprint(home_blueprint)
app.register_blueprint(admin_blueprint, url_prefix='/admin')
