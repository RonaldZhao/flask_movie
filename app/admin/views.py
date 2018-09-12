# 视图处理文件
from flask import render_template, redirect, url_for, flash, session, request
from functools import wraps

from . import admin
from app import db
from app.admin.forms import LoginForm, TagForm
from app.models import Admin, Tag


# 访问控制装饰器
def admin_login_required(func):
    @wraps(func)
    def deco(*args, **kwargs):
        if 'admin' not in session:
            return redirect(url_for('admin.login', next=request.url))
        return func(*args, **kwargs)
    return deco


@admin.route('/')
@admin_login_required
def index():
    return render_template('admin/index.html')


# 登录
@admin.route('/login/', methods=['GET', 'POST'])
def login():
    # TODO: 在已登录状态访问此页面跳转到主页或当前页
    form = LoginForm()
    if form.validate_on_submit():
        data = form.data
        admin = Admin.query.filter_by(name=data['account']).first()
        if not admin.check_pwd(data['pwd']):
            flash('密码错误!')
            return redirect(url_for('admin.login'))
        session['admin'] = data['account']
        return redirect(request.args.get('next') or url_for('admin.index'))
    return render_template('admin/login.html', form=form)


# 退出
@admin.route('/logout/')
@admin_login_required
def logout():
    session.pop('admin', None)
    return redirect(url_for('admin.login'))


# 修改密码
@admin.route('/pwd/')
@admin_login_required
def pwd():
    return render_template('admin/pwd.html')


# 添加标签
@admin.route('/tag/add/', methods=['GET', 'POST'])
@admin_login_required
def tag_add():
    form = TagForm()
    if form.validate_on_submit():
        data = form.data
        tag = Tag.query.filter_by(name=data['name']).count()
        if tag == 1:
            flash('标签"{0}"已经存在!'.format(data['name']), 'err')
            return redirect(url_for('admin.tag_add'))
        tag = Tag(name=data['name'])
        db.session.add(tag)
        db.session.commit()
        flash('标签"{0}"添加成功!'.format(data['name']), 'ok')
        return redirect(url_for('admin.tag_add'))
    return render_template('admin/tag_add.html', form=form)


# 标签列表
@admin.route('/tag/list/')
@admin_login_required
def tag_list():
    return render_template('admin/tag_list.html')


# 添加电影
@admin.route('/movie/add/')
@admin_login_required
def movie_add():
    return render_template('admin/movie_add.html')


# 电影列表
@admin.route('/movie/list/')
@admin_login_required
def movie_list():
    return render_template('admin/movie_list.html')


# 添加上映预告
@admin.route('/preview/add/')
@admin_login_required
def preview_add():
    return render_template('admin/preview_add.html')


# 上映预告列表
@admin.route('/preview/list/')
@admin_login_required
def preview_list():
    return render_template('admin/preview_list.html')


# 用户列表
@admin.route('/user/list/')
@admin_login_required
def user_list():
    return render_template('admin/user_list.html')


# 查看用户
@admin.route('/user/view/')
@admin_login_required
def user_view():
    return render_template('admin/user_view.html')


# 评论列表
@admin.route('/comment/list/')
@admin_login_required
def comment_list():
    return render_template('admin/comment_list.html')


# 收藏列表
@admin.route('/moviecol/list/')
@admin_login_required
def moviecol_list():
    return render_template('admin/moviecol_list.html')


# 操作日志列表
@admin.route('/oplog/list')
@admin_login_required
def oplog_list():
    return render_template('admin/oplog_list.html')


# 管理员日志列表
@admin.route('/adminloginlog/list')
@admin_login_required
def adminloginlog_list():
    return render_template('admin/adminloginlog_list.html')


# 用户日志列表
@admin.route('/userloginlog/list')
@admin_login_required
def userloginlog_list():
    return render_template('admin/userloginlog_list.html')


# 添加角色
@admin.route('/role/add/')
@admin_login_required
def role_add():
    return render_template('admin/role_add.html')


# 角色列表
@admin.route('/role/list/')
@admin_login_required
def role_list():
    return render_template('admin/role_list.html')


# 添加权限
@admin.route('/auth/add/')
@admin_login_required
def auth_add():
    return render_template('admin/auth_add.html')


# 权限列表
@admin.route('/auth/list/')
@admin_login_required
def auth_list():
    return render_template('admin/auth_list.html')


# 添加管理员
@admin.route('/admin/add/')
@admin_login_required
def admin_add():
    return render_template('admin/admin_add.html')


# 管理员列表
@admin.route('/admin/list/')
@admin_login_required
def admin_list():
    return render_template('admin/admin_list.html')
