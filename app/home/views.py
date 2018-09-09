# 视图处理文件
from flask import render_template

from . import home


@home.route('/')
def index():
    # return '<h1 style="color: green;">this is home.</h1>'
    return render_template('home/index.html')
