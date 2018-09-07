# 初始化脚本文件
from flask import Blueprint

admin = Blueprint('admin', __name__)

import app.admin.views
