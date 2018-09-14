# 视图处理文件
import os
import uuid
import datetime

from flask import render_template, redirect, url_for, flash, session, request
from functools import wraps
from werkzeug.utils import secure_filename

from . import admin
from app import db, app
from app.admin.forms import LoginForm, TagForm, MovieForm, PreviewForm, PwdForm
from app.models import Admin, Tag, Movie, Preview, User, Comment, Moviecol


# 访问控制装饰器
def admin_login_required(func):
    @wraps(func)
    def deco(*args, **kwargs):
        if 'admin' not in session:
            return redirect(url_for('admin.login', next=request.url))
        return func(*args, **kwargs)
    return deco


def change_filename(filename):
    filename_ext = os.path.splitext(filename)
    filename = datetime.datetime.now().strftime('%Y%m%d%H%M%S') + str(uuid.uuid4().hex) + filename_ext[-1]
    return filename


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
            flash('密码错误!', 'err')
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
@admin.route('/pwd/', methods=['GET', 'POST'])
@admin_login_required
def pwd():
    form = PwdForm()
    if form.validate_on_submit():
        data = form.data
        admin = Admin.query.filter_by(name=session['admin']).first()
        from werkzeug.security import generate_password_hash
        admin.pwd = generate_password_hash(data['new_pwd'])
        db.session.add(admin)
        db.session.commit()
        flash('密码修改成功! 请重新登录.', 'ok')
        return redirect(url_for('admin.logout'))
    return render_template('admin/pwd.html', form=form)


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


# 修改标签
@admin.route('/tag/edit/<int:id>/', methods=['GET', 'POST'])
@admin_login_required
def tag_edit(id=None):
    # TODO: 修改添加时间为修改时间
    tag = Tag.query.get_or_404(int(id))
    form = TagForm()
    if form.validate_on_submit():
        data = form.data
        # TODO: 在前端判断数据是否发生了修改, 发生修改了再提交到服务器处理, 减轻服务器压力
        if data['name'] == tag.name:
            flash('标签"{0}"未发生修改!'.format(data['name']), 'err')
            return redirect(url_for('admin.tag_edit', id=id))
        if Tag.query.filter_by(name=data['name']).count() == 1:
            flash('标签"{0}"已经存在!'.format(data['name']), 'err')
            return redirect(url_for('admin.tag_edit', id=id))
        flash('标签"{0}"已经被修改为"{1}"!'.format(tag.name, data['name']), 'ok')
        tag.name = data['name']
        db.session.add(tag)
        db.session.commit()
        return redirect(url_for('admin.tag_edit', id=id))
    return render_template('admin/tag_edit.html', form=form, tag=tag)


# 标签列表, 分页显示
@admin.route('/tag/list/<int:page>/', methods=['GET'])
@admin_login_required
def tag_list(page=None):
    if page is None:
        page = 1
    # TODO: 下面的按时间排序的方式在当时间相同的时候可能会有显示遗漏问题
    page_data = Tag.query.order_by(Tag.add_time.desc()).paginate(page=page, per_page=10)
    return render_template('admin/tag_list.html', page_data=page_data)


# 删除标签
@admin.route('/tag/delete/<int:id>/', methods=['GET'])
@admin_login_required
def tag_delete(id=None):
    if id:
        tag = Tag.query.filter_by(id=id).first_or_404()
        db.session.delete(tag)
        db.session.commit()
        flash('标签"{0}"删除成功!'.format(tag.name), 'ok')
    return redirect(url_for('admin.tag_list', page=1))


# 添加电影
@admin.route('/movie/add/', methods=['GET', 'POST'])
@admin_login_required
def movie_add():
    form = MovieForm()
    if form.validate_on_submit():
        data = form.data
        file_url = secure_filename(form.url.data.filename)
        file_logo = secure_filename(form.logo.data.filename)

        if not os.path.exists(app.config['UP_DIR']):
            os.makedirs(app.config['UP_DIR'])
            os.chmod(app.config['UP_DIR'], 'rw')

        url = change_filename(file_url)
        logo = change_filename(file_logo)
        form.url.data.save(app.config['UP_DIR'] + url)
        form.logo.data.save(app.config['UP_DIR'] + logo)

        movie = Movie(
            title=data['title'],
            url=url,
            info=data['info'],
            logo=logo,
            star=int(data['star']),
            playnum=0,
            commentnum=0,
            tag_id=int(data['tag_id']),
            area=data['area'],
            release_time=data['release_time'],
            length=data['length']
        )
        db.session.add(movie)
        db.session.commit()
        flash('电影"{0}"添加成功!'.format(data['title']), 'ok')
        return redirect(url_for('admin.movie_add'))
    return render_template('admin/movie_add.html', form=form)


# 删除电影
@admin.route('/movie/delete/<int:id>/', methods=['GET'])
@admin_login_required
def movie_delete(id=None):
    # TODO: 删除与其相关的其他数据(如评论, 收藏) and 删除电影视频和封面文件
    if id:
        movie = Movie.query.filter_by(id=id).first_or_404()
        db.session.delete(movie)
        db.session.commit()
        # TODO: 删除其资源
        flash('电影"{0}"删除成功!'.format(movie.title), 'ok')

    return redirect(url_for('admin.movie_list', page=1))


# 电影列表
@admin.route('/movie/list/<int:page>/', methods=['GET'])
@admin_login_required
def movie_list(page=None):
    if page is None:
        page = 1

    # TODO: 下面的按时间排序的方式在当时间相同的时候可能会有显示遗漏问题
    page_data = Movie.query.join(Tag).filter(
        Tag.id==Movie.tag_id
    ).order_by(
        Movie.add_time.desc()
    ).paginate(page=page, per_page=10)
    return render_template('admin/movie_list.html', page_data=page_data)


# 修改电影
@admin.route('/movie/edit/<int:id>/', methods=['GET', 'POST'])
@admin_login_required
def movie_edit(id=None):
    # TODO: 修改添加时间为修改时间
    movie = Movie.query.get_or_404(int(id))
    form = MovieForm()
    form.url.validators.clear()
    form.logo.validators.clear()
    if request.method == 'GET':
        form.info.data = movie.info
        form.tag_id.data = movie.tag_id
        form.star.data = movie.star
    if form.validate_on_submit():
        old_url = movie.url
        old_logo = movie.logo
        data = form.data
        changed = False
        # TODO: 在前端判断数据是否发生了修改, 发生修改了再提交到服务器处理, 减轻服务器压力
        movie_count = Movie.query.filter_by(title=data['title']).count()

        if data['title'] != movie.title:
            if movie_count >= 1:
                flash('此电影名称已经存在!', 'err')
                return redirect(url_for('admin.movie_edit', id=id))
            movie.title = data['title']
            changed = True

        if data['star'] != movie.star:
            movie.star = data['star']
            changed = True

        if data['tag_id'] != movie.tag_id:
            movie.tag_id = data['tag_id']
            changed = True

        if data['info'] != movie.info:
            movie.info = data['info']
            changed = True

        if data['area'] != movie.area:
            movie.area = data['area']
            changed = True

        if data['length'] != movie.length:
            movie.length = data['length']
            changed = True

        if data['release_time'] != str(movie.release_time):
            movie.release_time = data['release_time']
            changed = True

        if not os.path.exists(app.config['UP_DIR']):
            os.makedirs(app.config['UP_DIR'])
            os.chmod(app.config['UP_DIR'], 'rw')

        if type(form.url.data) != str and form.url.data.filename != "":
            file_url = secure_filename(form.url.data.filename)
            movie.url = change_filename(file_url)
            form.url.data.save(app.config['UP_DIR'] + movie.url)
            changed = True

        if type(form.logo.data) != str and form.logo.data.filename != "":
            file_logo = secure_filename(form.logo.data.filename)
            movie.logo = change_filename(file_logo)
            form.logo.data.save(app.config['UP_DIR'] + movie.logo)
            changed = True

        if changed:
            db.session.add(movie)
            db.session.commit()
            # 下面这两个删除就资源可能发生其他请求正在读取的时候无法删除的情况
            if movie.url != old_url:
                os.remove(app.config['UP_DIR'] + old_url)
            if movie.logo != old_logo:
                os.remove(app.config['UP_DIR'] + old_logo)
            flash('电影信息修改成功!', 'ok')
        else:
            flash('亲, 没改信息就不要点保存了嘛!', 'err')
        return redirect(url_for('admin.movie_edit', id=id))
    return render_template('admin/movie_edit.html', form=form, movie=movie)


# 添加上映预告
@admin.route('/preview/add/', methods=['GET', 'POST'])
@admin_login_required
def preview_add():
    form = PreviewForm()
    if form.validate_on_submit():
        data = form.data
        preview_count = Preview.query.filter_by(title=data['title']).count()

        if preview_count >= 1:
            flash('预告片"{0}"已经存在!'.format(data['title']), 'err')
            return redirect(url_for('admin.preview_add'))

        file_logo = secure_filename(form.logo.data.filename)

        if not os.path.exists(app.config['UP_DIR']):
            os.makedirs(app.config['UP_DIR'])
            os.chmod(app.config['UP_DIR'], 'rw')

        logo = change_filename(file_logo)
        form.logo.data.save(app.config['UP_DIR'] + logo)
        preview = Preview(
            title=data['title'],
            logo=logo
        )
        db.session.add(preview)
        db.session.commit()
        flash('电影预告"{0}"添加成功!'.format(preview.title), 'ok')
        return redirect(url_for('admin.preview_add'))
    return render_template('admin/preview_add.html', form=form)


# 删除预告
@admin.route('/preview/delete/<int:id>/', methods=['GET'])
@admin_login_required
def preview_delete(id=None):
    if id:
        preview = Preview.query.get_or_404(int(id))
        old_logo = preview.logo
        db.session.delete(preview)
        db.session.commit()
        # 同时删除其封面图
        os.remove(app.config['UP_DIR'] + old_logo)
        flash('影片预告"{0}"删除成功!'.format(preview.title), 'ok')

    return redirect(url_for('admin.preview_list', page=1))


# 上映预告列表
@admin.route('/preview/list/<int:page>/')
@admin_login_required
def preview_list(page=None):
    if not page:
        page = 1
    page_data = Preview.query.order_by(Preview.add_time.desc()).paginate(page=page, per_page=10)
    return render_template('admin/preview_list.html', page_data=page_data)


# 修改预告
@admin.route('/preview/edit/<int:id>/', methods=['GET', 'POST'])
@admin_login_required
def preview_edit(id=None):
    # TODO: 修改添加时间为修改时间
    preview = Preview.query.get_or_404(int(id))
    form = PreviewForm()
    form.logo.validators.clear()
    if form.validate_on_submit():
        data = form.data
        # TODO: 在前端判断数据是否发生了修改, 发生修改了再提交到服务器处理, 减轻服务器压力
        if data['title'] == preview.title and type(form.logo.data) == str:
            flash('亲, 没改信息就不要点保存了嘛!', 'err')
            return redirect(url_for('admin.preview_edit', id=id))
        if data['title'] != preview.title and Preview.query.filter_by(title=data['title']).count() == 1:
            flash('影片预告"{0}"已经存在!'.format(data['title']), 'err')
            return redirect(url_for('admin.preview_edit', id=id))

        changed = False
        old_logo = preview.logo
        if type(form.logo.data) != str and form.logo.data.filename != "":
            file_logo = secure_filename(form.logo.data.filename)
            preview.logo = change_filename(file_logo)
            form.logo.data.save(app.config['UP_DIR'] + preview.logo)
            changed = True

        preview.title = data['title']
        db.session.add(preview)
        db.session.commit()
        flash('影片预告信息修改成功!', 'ok')

        if changed:
            os.remove(app.config['UP_DIR'] + old_logo)

        return redirect(url_for('admin.preview_edit', id=id))
    return render_template('admin/preview_edit.html', form=form, preview=preview)


# 用户列表
@admin.route('/user/list/<int:page>/')
@admin_login_required
def user_list(page=None):
    if page is None:
        page = 1
    page_data = User.query.order_by(User.register_time.desc()).paginate(page=page, per_page=10)
    return render_template('admin/user_list.html', page_data=page_data)


# 删除用户
@admin.route('/user/delete/<int:id>/', methods=['GET'])
@admin_login_required
def user_delete(id=None):
    if id:
        user = User.query.get_or_404(int(id))
        old_face = user.face
        db.session.delete(user)
        db.session.commit()
        # 同时删除其封面图
        if old_face != '' and os.path.exists(app.config['UP_DIR'] + 'user_faces'):
            os.remove(app.config['UP_DIR'] + 'user_faces/' + old_face)
        flash('用户"{0}"删除成功!'.format(user.email), 'ok')

    return redirect(url_for('admin.user_list', page=1))


# 查看用户
@admin.route('/user/view/<int:id>/', methods=['GET'])
@admin_login_required
def user_view(id=None):
    if id:
        user = User.query.get_or_404(int(id))
    return render_template('admin/user_view.html', user=user)


# 评论列表
@admin.route('/comment/list/<int:page>/', methods=['GET'])
@admin_login_required
def comment_list(page=None):
    if page is None:
        page = 1
    page_data = Comment.query.join(
        Movie
    ).join(
        User
    ).filter(
        Movie.id == Comment.movie_id,
        User.id == Comment.user_id
    ).order_by(
        Comment.add_time.desc()
    ).paginate(page=page, per_page=10)
    return render_template('admin/comment_list.html', page_data=page_data)


# 删除评论
@admin.route('/comment/delete/<int:id>/', methods=['GET'])
@admin_login_required
def comment_delete(id=None):
    if id:
        comment = Comment.query.get_or_404(int(id))
        db.session.delete(comment)
        db.session.commit()
        flash('删除评论成功!', 'ok')
    return redirect(url_for('admin.comment_list', page=1))

# 收藏列表
@admin.route('/moviecol/list/<int:page>/', methods=['GET'])
@admin_login_required
def moviecol_list(page=None):
    if page is None:
        page = 1
    page_data = Moviecol.query.join(
        Movie
    ).join(
        User
    ).filter(
        Movie.id == Moviecol.movie_id,
        User.id == Moviecol.user_id
    ).order_by(
        Moviecol.add_time.desc()
    ).paginate(page=page, per_page=10)
    return render_template('admin/moviecol_list.html', page_data=page_data)

@admin.route('/moviecol/delete/<int:id>/', methods=['GET'])
@admin_login_required
def moviecol_delete(id=None):
    if id:
        moviecol = Moviecol.query.get_or_404(int(id))
        db.session.delete(moviecol)
        db.session.commit()
        flash('删除收藏成功!', 'ok')
    return redirect(url_for('admin.moviecol_list'))


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
