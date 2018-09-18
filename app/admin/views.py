# 视图处理文件
import os
import stat
import uuid
import datetime

from flask import (
    render_template,
    redirect,
    url_for,
    flash,
    session,
    request,
    abort,
)
from functools import wraps
from werkzeug.utils import secure_filename

from . import admin
from app import db, app
from app.admin.forms import (
    LoginForm,
    TagForm,
    MovieForm,
    PreviewForm,
    PwdForm,
    AuthForm,
    RoleForm,
    AdminForm,
)
from app.models import (
    Admin,
    Tag,
    Movie,
    Preview,
    User,
    Comment,
    Moviecol,
    AdminLog,
    UserLog,
    OpLog,
    Auth,
    Role,
)


@admin.context_processor
def login_time():
    """
    用来显示每个页面的访问时间
    """
    data = dict(
        login_time=datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    )
    return data


# 访问控制装饰器
def admin_login_required(func):
    @wraps(func)
    def deco(*args, **kwargs):
        if "admin" not in session:
            return redirect(url_for("admin.login", next=request.url))
        return func(*args, **kwargs)

    return deco


def admin_auth(func):
    @wraps(func)
    def deco(*args, **kwargs):
        admin = (
            Admin.query.join(Role)
            .filter(Admin.id == session["admin_id"], Role.id == Admin.role_id)
            .first()
        )
        if admin.is_super == 1:  # 如果是普通管理员才进行权限控制
            auths = admin.role.auths
            auths = list(map(int, auths.split(",")))
            auth_list = Auth.query.all()
            urls = [
                auth.url for auth in auth_list for a in auths if a == auth.id
            ]
            rule = request.url_rule
            if not str(rule) in urls:
                abort(404)
        return func(*args, **kwargs)

    return deco


def change_filename(filename):
    filename_ext = os.path.splitext(filename)
    filename = (
        datetime.datetime.now().strftime("%Y%m%d%H%M%S")
        + str(uuid.uuid4().hex)
        + filename_ext[-1]
    )
    return filename


@admin.route("/")
@admin_login_required
def index():
    return render_template("admin/index.html")


# 登录
@admin.route("/login/", methods=["GET", "POST"])
def login():
    # TODO: 在已登录状态访问此页面跳转到主页或当前页
    form = LoginForm()
    if form.validate_on_submit():
        data = form.data
        admin = Admin.query.filter_by(name=data["account"]).first()
        if not admin.check_pwd(data["pwd"]):
            flash("密码错误!", "err")
            return redirect(url_for("admin.login"))
        session["admin"] = data["account"]
        session["admin_id"] = admin.id
        adminlog = AdminLog(admin_id=admin.id, ip=request.remote_addr)
        db.session.add(adminlog)
        db.session.commit()
        return redirect(request.args.get("next") or url_for("admin.index"))
    return render_template("admin/login.html", form=form)


# 退出
@admin.route("/logout/")
@admin_login_required
def logout():
    session.pop("admin", None)
    session.pop("admin_id", None)
    return redirect(url_for("admin.login"))


# 修改密码
@admin.route("/pwd/", methods=["GET", "POST"])
@admin_login_required
def pwd():
    form = PwdForm()
    if form.validate_on_submit():
        data = form.data
        admin = Admin.query.filter_by(name=session["admin"]).first()
        from werkzeug.security import generate_password_hash

        admin.pwd = generate_password_hash(data["new_pwd"])
        db.session.add(admin)
        oplog = OpLog(
            admin_id=session["admin_id"], ip=request.remote_addr, reason="修改密码"
        )
        db.session.add(oplog)
        db.session.commit()
        flash("密码修改成功! 请重新登录.", "ok")
        return redirect(url_for("admin.logout"))
    return render_template("admin/pwd.html", form=form)


# 添加标签
@admin.route("/tag/add/", methods=["GET", "POST"])
@admin_login_required
@admin_auth
def tag_add():
    form = TagForm()
    if form.validate_on_submit():
        data = form.data
        tag = Tag.query.filter_by(name=data["name"]).count()
        if tag == 1:
            flash('标签"{0}"已经存在!'.format(data["name"]), "err")
            return redirect(url_for("admin.tag_add"))
        tag = Tag(name=data["name"])
        db.session.add(tag)
        oplog = OpLog(
            admin_id=session["admin_id"],
            ip=request.remote_addr,
            reason='添加标签"{0}"'.format(data["name"]),
        )
        db.session.add(oplog)
        db.session.commit()
        flash('标签"{0}"添加成功!'.format(data["name"]), "ok")
        return redirect(url_for("admin.tag_add"))
    return render_template("admin/tag_add.html", form=form)


# 修改标签
@admin.route("/tag/edit/<int:id>/", methods=["GET", "POST"])
@admin_login_required
@admin_auth
def tag_edit(id=None):
    # TODO: 修改添加时间为修改时间
    tag = Tag.query.get_or_404(int(id))
    form = TagForm()
    if form.validate_on_submit():
        data = form.data
        # TODO: 在前端判断数据是否发生了修改, 发生修改了再提交到服务器处理, 减轻服务器压力
        if data["name"] == tag.name:
            flash('标签"{0}"未发生修改!'.format(data["name"]), "err")
            return redirect(url_for("admin.tag_edit", id=id))
        if Tag.query.filter_by(name=data["name"]).count() == 1:
            flash('标签"{0}"已经存在!'.format(data["name"]), "err")
            return redirect(url_for("admin.tag_edit", id=id))
        flash('标签"{0}"已经被修改为"{1}"!'.format(tag.name, data["name"]), "ok")
        oplog = OpLog(
            admin_id=session["admin_id"],
            ip=request.remote_addr,
            reason='修改标签"{0}"为"{1}"'.format(tag.name, data["name"]),
        )
        tag.name = data["name"]
        db.session.add(tag)
        db.session.add(oplog)
        db.session.commit()
        return redirect(url_for("admin.tag_edit", id=id))
    return render_template("admin/tag_edit.html", form=form, tag=tag)


# 标签列表, 分页显示
@admin.route("/tag/list/<int:page>/", methods=["GET"])
@admin_login_required
@admin_auth
def tag_list(page=None):
    if page is None:
        page = 1
    # TODO: 下面的按时间排序的方式在当时间相同的时候可能会有显示遗漏问题
    page_data = Tag.query.order_by(Tag.add_time.desc()).paginate(
        page=page, per_page=10
    )
    return render_template("admin/tag_list.html", page_data=page_data)


# 删除标签
@admin.route("/tag/delete/<int:id>/", methods=["GET"])
@admin_login_required
@admin_auth
def tag_delete(id=None):
    if id:
        tag = Tag.query.filter_by(id=id).first_or_404()
        db.session.delete(tag)
        oplog = OpLog(
            admin_id=session["admin_id"],
            ip=request.remote_addr,
            reason='删除标签"{0}"'.format(tag.name),
        )
        db.session.add(oplog)
        db.session.commit()
        flash('标签"{0}"删除成功!'.format(tag.name), "ok")
    return redirect(url_for("admin.tag_list", page=1))


# 添加电影
@admin.route("/movie/add/", methods=["GET", "POST"])
@admin_login_required
@admin_auth
def movie_add():
    form = MovieForm()
    if form.validate_on_submit():
        data = form.data
        file_url = secure_filename(form.url.data.filename)
        file_logo = secure_filename(form.logo.data.filename)

        if not os.path.exists(app.config["UP_DIR"]):
            os.makedirs(app.config["UP_DIR"])
            os.chmod(app.config["UP_DIR"], stat.S_IRWXU)

        url = change_filename(file_url)
        logo = change_filename(file_logo)
        form.url.data.save(app.config["UP_DIR"] + url)
        form.logo.data.save(app.config["UP_DIR"] + logo)

        movie = Movie(
            title=data["title"],
            url=url,
            info=data["info"],
            logo=logo,
            star=int(data["star"]),
            playnum=0,
            commentnum=0,
            tag_id=int(data["tag_id"]),
            area=data["area"],
            release_time=data["release_time"],
            length=data["length"],
        )
        db.session.add(movie)
        oplog = OpLog(
            admin_id=session["admin_id"],
            ip=request.remote_addr,
            reason='添加电影"{0}"'.format(movie.title),
        )
        db.session.add(oplog)
        db.session.commit()
        flash('电影"{0}"添加成功!'.format(data["title"]), "ok")
        return redirect(url_for("admin.movie_add"))
    return render_template("admin/movie_add.html", form=form)


# 删除电影
@admin.route("/movie/delete/<int:id>/", methods=["GET"])
@admin_login_required
@admin_auth
def movie_delete(id=None):
    # TODO: 删除与其相关的其他数据(如评论, 收藏) and 删除电影视频和封面文件
    if id:
        movie = Movie.query.filter_by(id=id).first_or_404()
        db.session.delete(movie)
        oplog = OpLog(
            admin_id=session["admin_id"],
            ip=request.remote_addr,
            reason='删除电影"{0}"'.format(movie.title),
        )
        db.session.add(oplog)
        db.session.commit()
        # 删除其资源
        if os.path.exists(app.config["UP_DIR"] + movie.url):
            os.remove(app.config["UP_DIR"] + movie.url)
        if os.path.exists(app.config["UP_DIR"] + movie.logo):
            os.remove(app.config["UP_DIR"] + movie.logo)
        flash('电影"{0}"删除成功!'.format(movie.title), "ok")

    return redirect(url_for("admin.movie_list", page=1))


# 电影列表
@admin.route("/movie/list/<int:page>/", methods=["GET"])
@admin_login_required
@admin_auth
def movie_list(page=None):
    if page is None:
        page = 1

    # TODO: 下面的按时间排序的方式在当时间相同的时候可能会有显示遗漏问题
    page_data = (
        Movie.query.join(Tag)
        .filter(Tag.id == Movie.tag_id)
        .order_by(Movie.add_time.desc())
        .paginate(page=page, per_page=10)
    )
    return render_template("admin/movie_list.html", page_data=page_data)


# 修改电影
@admin.route("/movie/edit/<int:id>/", methods=["GET", "POST"])
@admin_login_required
@admin_auth
def movie_edit(id=None):
    # TODO: 修改添加时间为修改时间
    movie = Movie.query.get_or_404(int(id))
    form = MovieForm()
    form.url.validators.clear()
    form.logo.validators.clear()
    if request.method == "GET":
        form.info.data = movie.info
        form.tag_id.data = movie.tag_id
        form.star.data = movie.star
    if form.validate_on_submit():
        old_url = movie.url
        old_logo = movie.logo
        data = form.data
        changed = False
        # TODO: 在前端判断数据是否发生了修改, 发生修改了再提交到服务器处理, 减轻服务器压力
        movie_count = Movie.query.filter_by(title=data["title"]).count()

        if data["title"] != movie.title:
            if movie_count >= 1:
                flash("此电影名称已经存在!", "err")
                return redirect(url_for("admin.movie_edit", id=id))
            movie.title = data["title"]
            changed = True

        if data["star"] != movie.star:
            movie.star = data["star"]
            changed = True

        if data["tag_id"] != movie.tag_id:
            movie.tag_id = data["tag_id"]
            changed = True

        if data["info"] != movie.info:
            movie.info = data["info"]
            changed = True

        if data["area"] != movie.area:
            movie.area = data["area"]
            changed = True

        if data["length"] != movie.length:
            movie.length = data["length"]
            changed = True

        if data["release_time"] != str(movie.release_time):
            movie.release_time = data["release_time"]
            changed = True

        if not os.path.exists(app.config["UP_DIR"]):
            os.makedirs(app.config["UP_DIR"])
            os.chmod(app.config["UP_DIR"], stat.S_IRWXU)

        if type(form.url.data) != str and form.url.data.filename != "":
            file_url = secure_filename(form.url.data.filename)
            movie.url = change_filename(file_url)
            form.url.data.save(app.config["UP_DIR"] + movie.url)
            changed = True

        if type(form.logo.data) != str and form.logo.data.filename != "":
            file_logo = secure_filename(form.logo.data.filename)
            movie.logo = change_filename(file_logo)
            form.logo.data.save(app.config["UP_DIR"] + movie.logo)
            changed = True

        if changed:
            db.session.add(movie)
            oplog = OpLog(
                admin_id=session["admin_id"],
                ip=request.remote_addr,
                reason='修改电影"{0}"的信息'.format(movie.title),
            )
            db.session.add(oplog)
            db.session.commit()
            # 下面这两个删除就资源可能发生其他请求正在读取的时候无法删除的情况
            if movie.url != old_url:
                os.remove(app.config["UP_DIR"] + old_url)
            if movie.logo != old_logo:
                os.remove(app.config["UP_DIR"] + old_logo)
            flash("电影信息修改成功!", "ok")
        else:
            flash("亲, 没改信息就不要点保存了嘛!", "err")
        return redirect(url_for("admin.movie_edit", id=id))
    return render_template("admin/movie_edit.html", form=form, movie=movie)


# 添加上映预告
@admin.route("/preview/add/", methods=["GET", "POST"])
@admin_login_required
@admin_auth
def preview_add():
    form = PreviewForm()
    if form.validate_on_submit():
        data = form.data
        preview_count = Preview.query.filter_by(title=data["title"]).count()

        if preview_count >= 1:
            flash('预告片"{0}"已经存在!'.format(data["title"]), "err")
            return redirect(url_for("admin.preview_add"))

        file_logo = secure_filename(form.logo.data.filename)

        if not os.path.exists(app.config["UP_DIR"]):
            os.makedirs(app.config["UP_DIR"])
            os.chmod(app.config["UP_DIR"], stat.S_IRWXU)

        logo = change_filename(file_logo)
        form.logo.data.save(app.config["UP_DIR"] + logo)
        preview = Preview(title=data["title"], logo=logo)
        db.session.add(preview)
        oplog = OpLog(
            admin_id=session["admin_id"],
            ip=request.remote_addr,
            reason='添加电影预告"{0}"'.format(data["title"]),
        )
        db.session.add(oplog)
        db.session.commit()
        flash('电影预告"{0}"添加成功!'.format(preview.title), "ok")
        return redirect(url_for("admin.preview_add"))
    return render_template("admin/preview_add.html", form=form)


# 删除预告
@admin.route("/preview/delete/<int:id>/", methods=["GET"])
@admin_login_required
@admin_auth
def preview_delete(id=None):
    if id:
        preview = Preview.query.get_or_404(int(id))
        old_logo = preview.logo
        db.session.delete(preview)
        oplog = OpLog(
            admin_id=session["admin_id"],
            ip=request.remote_addr,
            reason='删除电影预告"{0}"'.format(preview.title),
        )
        db.session.add(oplog)
        db.session.commit()
        # 同时删除其封面图
        os.remove(app.config["UP_DIR"] + old_logo)
        flash('影片预告"{0}"删除成功!'.format(preview.title), "ok")

    return redirect(url_for("admin.preview_list", page=1))


# 上映预告列表
@admin.route("/preview/list/<int:page>/")
@admin_login_required
@admin_auth
def preview_list(page=None):
    if not page:
        page = 1
    page_data = Preview.query.order_by(Preview.add_time.desc()).paginate(
        page=page, per_page=10
    )
    return render_template("admin/preview_list.html", page_data=page_data)


# 修改预告
@admin.route("/preview/edit/<int:id>/", methods=["GET", "POST"])
@admin_login_required
@admin_auth
def preview_edit(id=None):
    # TODO: 修改添加时间为修改时间
    preview = Preview.query.get_or_404(int(id))
    form = PreviewForm()
    form.logo.validators.clear()
    if form.validate_on_submit():
        data = form.data
        # TODO: 在前端判断数据是否发生了修改, 发生修改了再提交到服务器处理, 减轻服务器压力
        if data["title"] == preview.title and type(form.logo.data) == str:
            flash("亲, 没改信息就不要点保存了嘛!", "err")
            return redirect(url_for("admin.preview_edit", id=id))
        if (
            data["title"] != preview.title
            and Preview.query.filter_by(title=data["title"]).count() == 1
        ):
            flash('影片预告"{0}"已经存在!'.format(data["title"]), "err")
            return redirect(url_for("admin.preview_edit", id=id))

        changed = False
        old_logo = preview.logo
        if type(form.logo.data) != str and form.logo.data.filename != "":
            file_logo = secure_filename(form.logo.data.filename)
            preview.logo = change_filename(file_logo)
            form.logo.data.save(app.config["UP_DIR"] + preview.logo)
            changed = True

        preview.title = data["title"]
        db.session.add(preview)
        oplog = OpLog(
            admin_id=session["admin_id"],
            ip=request.remote_addr,
            reason='修改电影预告"{0}"的信息'.format(preview.title),
        )
        db.session.add(oplog)
        db.session.commit()
        flash("影片预告信息修改成功!", "ok")

        if changed:
            os.remove(app.config["UP_DIR"] + old_logo)

        return redirect(url_for("admin.preview_edit", id=id))
    return render_template(
        "admin/preview_edit.html", form=form, preview=preview
    )


# 用户列表
@admin.route("/user/list/<int:page>/")
@admin_login_required
@admin_auth
def user_list(page=None):
    if page is None:
        page = 1
    page_data = User.query.order_by(User.register_time.desc()).paginate(
        page=page, per_page=10
    )
    return render_template("admin/user_list.html", page_data=page_data)


# 删除用户
@admin.route("/user/delete/<int:id>/", methods=["GET"])
@admin_login_required
@admin_auth
def user_delete(id=None):
    if id:
        user = User.query.get_or_404(int(id))
        old_face = user.face
        db.session.delete(user)
        oplog = OpLog(
            admin_id=session["admin_id"],
            ip=request.remote_addr,
            reason='删除用户"{0}"'.format(user.name),
        )
        db.session.add(oplog)
        db.session.commit()
        # 同时删除其封面图
        if old_face != "" and os.path.exists(
            app.config["UP_DIR"] + "user_faces"
        ):
            os.remove(app.config["UP_DIR"] + "user_faces/" + old_face)
        flash('用户"{0}"删除成功!'.format(user.email), "ok")

    return redirect(url_for("admin.user_list", page=1))


# 查看用户
@admin.route("/user/view/<int:id>/", methods=["GET"])
@admin_login_required
@admin_auth
def user_view(id=None):
    if id:
        user = User.query.get_or_404(int(id))
    return render_template("admin/user_view.html", user=user)


# 评论列表
@admin.route("/comment/list/<int:page>/", methods=["GET"])
@admin_login_required
@admin_auth
def comment_list(page=None):
    if page is None:
        page = 1
    page_data = (
        Comment.query.join(Movie)
        .join(User)
        .filter(Movie.id == Comment.movie_id, User.id == Comment.user_id)
        .order_by(Comment.add_time.desc())
        .paginate(page=page, per_page=10)
    )
    return render_template("admin/comment_list.html", page_data=page_data)


# 删除评论
@admin.route("/comment/delete/<int:id>/", methods=["GET"])
@admin_login_required
@admin_auth
def comment_delete(id=None):
    if id:
        comment = Comment.query.get_or_404(int(id))
        db.session.delete(comment)
        movie = Movie.query.filter_by(id=comment.movie_id).first()
        user = User.query.filter_by(id=comment.user_id).first()
        oplog = OpLog(
            admin_id=session["admin_id"],
            ip=request.remote_addr,
            reason='删除{0}用户"{0}"在电影"{1}"的评论'.format(
                comment.add_time, user.name, movie.title
            ),
        )
        db.session.add(oplog)
        db.session.commit()
        flash("删除评论成功!", "ok")
    return redirect(url_for("admin.comment_list", page=1))


# 收藏列表
@admin.route("/moviecol/list/<int:page>/", methods=["GET"])
@admin_login_required
@admin_auth
def moviecol_list(page=None):
    if page is None:
        page = 1
    page_data = (
        Moviecol.query.join(Movie)
        .join(User)
        .filter(Movie.id == Moviecol.movie_id, User.id == Moviecol.user_id)
        .order_by(Moviecol.add_time.desc())
        .paginate(page=page, per_page=10)
    )
    return render_template("admin/moviecol_list.html", page_data=page_data)


@admin.route("/moviecol/delete/<int:id>/", methods=["GET"])
@admin_login_required
@admin_auth
def moviecol_delete(id=None):
    if id:
        moviecol = Moviecol.query.get_or_404(int(id))
        db.session.delete(moviecol)
        movie = Movie.query.filter_by(id=moviecol.movie_id).first()
        user = User.query.filter_by(id=moviecol.user_id).first()
        oplog = OpLog(
            admin_id=session["admin_id"],
            ip=request.remote_addr,
            reason='删除用户"{0}"收藏的电影"{1}"'.format(user.name, movie.title),
        )
        db.session.add(oplog)
        db.session.commit()
        flash("删除收藏成功!", "ok")
    return redirect(url_for("admin.moviecol_list"))


# 操作日志列表
@admin.route("/oplog/list/<int:page>/")
@admin_login_required
@admin_auth
def oplog_list(page=None):
    if page is None:
        page = 1
    page_data = (
        OpLog.query.join(Admin)
        .filter(OpLog.admin_id == Admin.id)
        .order_by(OpLog.add_time.desc())
        .paginate(page=page, per_page=10)
    )
    return render_template("admin/oplog_list.html", page_data=page_data)


# 管理员日志列表
@admin.route("/adminloginlog/list/<int:page>/", methods=["GET"])
@admin_login_required
@admin_auth
def adminloginlog_list(page=None):
    if not page:
        page = 1
    page_data = (
        AdminLog.query.join(Admin)
        .filter(AdminLog.admin_id == Admin.id)
        .order_by(AdminLog.login_time.desc())
        .paginate(page=page, per_page=10)
    )
    return render_template("admin/adminloginlog_list.html", page_data=page_data)


# 用户日志列表
@admin.route("/userloginlog/list/<int:page>/")
@admin_login_required
@admin_auth
def userloginlog_list(page=None):
    if page is None:
        page = 1
    page_data = (
        UserLog.query.join(User)
        .filter(UserLog.user_id == User.id)
        .order_by(UserLog.login_time.desc())
        .paginate(page=page, per_page=10)
    )

    return render_template("admin/userloginlog_list.html", page_data=page_data)


# 添加角色
@admin.route("/role/add/", methods=["GET", "POST"])
@admin_login_required
@admin_auth
def role_add():
    form = RoleForm()
    if form.validate_on_submit():
        data = form.data
        if Role.query.filter_by(name=data["name"]).count() == 1:
            flash('角色"{0}"已存在，请勿重复添加！'.format(data["name"]), "err")
            return redirect(url_for("admin.role_add"))
        role = Role(name=data["name"], auths=",".join(map(str, data["auths"])))
        db.session.add(role)
        oplog = OpLog(
            admin_id=session["admin_id"],
            ip=request.remote_addr,
            reason='添加角色"{0}"'.format(data["name"]),
        )
        db.session.add(oplog)
        db.session.commit()
        flash('添加角色"{0}"成功！'.format(data["name"]), "ok")
        return redirect(url_for("admin.role_add"))
    return render_template("admin/role_add.html", form=form)


# 角色删除
@admin.route("/role/delete/<int:id>/", methods=["GET"])
@admin_login_required
@admin_auth
def role_delete(id=None):
    if id:
        role = Role.query.get_or_404(int(id))
        db.session.delete(role)
        oplog = OpLog(
            admin_id=session["admin_id"],
            ip=request.remote_addr,
            reason='删除角色"{0}"'.format(role.name),
        )
        db.session.add(oplog)
        db.session.commit()
        flash('删除角色"{0}"成功！'.format(role.name), "ok")
    return redirect(url_for("admin.role_list", page=1))


# 角色列表
@admin.route("/role/list/<int:page>/", methods=["GET"])
@admin_login_required
@admin_auth
def role_list(page=None):
    if page is None:
        page = 1
    page_data = Role.query.order_by(Role.add_time.desc()).paginate(
        page=page, per_page=10
    )
    return render_template("admin/role_list.html", page_data=page_data)


# 修改角色
@admin.route("/role/edit/<int:id>/", methods=["GET", "POST"])
@admin_login_required
@admin_auth
def role_edit(id=None):
    form = RoleForm()
    role = Role.query.get_or_404(int(id))
    if request.method == "GET":
        form.auths.data = list(map(int, role.auths.split(",")))
    if form.validate_on_submit():
        data = form.data
        if data["name"] == role.name and data["auths"] == list(
            map(int, role.auths.split(","))
        ):
            flash("老板，您未作修改哟~", "err")
            return redirect(url_for("admin.role_edit", id=id))
        role.name = data["name"]
        role.auths = ",".join(map(str, data["auths"]))
        db.session.add(role)
        oplog = OpLog(
            admin_id=session["admin_id"],
            ip=request.remote_addr,
            reason='修改角色"{0}"的信息'.format(data["name"]),
        )
        db.session.add(oplog)
        db.session.commit()
        flash("角色信息修改成功！", "ok")
        return redirect(url_for("admin.role_edit", id=id))
    return render_template("admin/role_edit.html", form=form, role=role)


# 添加权限
@admin.route("/auth/add/", methods=["GET", "POST"])
@admin_login_required
@admin_auth
def auth_add():
    form = AuthForm()
    if form.validate_on_submit():
        data = form.data
        auth = Auth(name=data["name"], url=data["url"])
        if Auth.query.filter_by(name=data["name"]).count() == 1:
            flash('权限"{0}"已经存在，请勿重复添加！'.format(data["name"]), "err")
        else:
            db.session.add(auth)
            oplog = OpLog(
                admin_id=session["admin_id"],
                ip=request.remote_addr,
                reason='添加权限"{0}"'.format(auth.name),
            )
            db.session.add(oplog)
            db.session.commit()
            flash('添加权限"{0}"成功！'.format(data["name"]), "ok")
        return redirect(url_for("admin.auth_add"))
    return render_template("admin/auth_add.html", form=form)


# 删除权限
@admin.route("/auth/delete/<int:id>/", methods=["GET"])
@admin_login_required
@admin_auth
def auth_delete(id=None):
    if id:
        auth = Auth.query.filter_by(id=id).first_or_404()
        db.session.delete(auth)
        oplog = OpLog(
            admin_id=session["admin_id"],
            ip=request.remote_addr,
            reason='删除权限"{0}"'.format(auth.name),
        )
        db.session.add(oplog)
        db.session.commit()
        flash('权限"{0}"删除成功!'.format(auth.name), "ok")
    return redirect(url_for("admin.auth_list", page=1))


# 权限列表
@admin.route("/auth/list/<int:page>/", methods=["GET"])
@admin_login_required
@admin_auth
def auth_list(page=None):
    if page is None:
        page = 1
    page_data = Auth.query.order_by(Auth.add_time.desc()).paginate(
        page=page, per_page=10
    )
    return render_template("admin/auth_list.html", page_data=page_data)


# 修改权限信息
@admin.route("/auth/edit/<int:id>/", methods=["GET", "POST"])
@admin_login_required
@admin_auth
def auth_edit(id=None):
    # TODO: 修改添加时间为修改时间
    auth = Auth.query.get_or_404(int(id))
    form = AuthForm()
    if form.validate_on_submit():
        data = form.data
        # TODO: 在前端判断数据是否发生了修改, 发生修改了再提交到服务器处理, 减轻服务器压力
        if data["name"] == auth.name and data["url"] == auth.url:
            flash("权限信息不作修改就不要点点点了嘛!", "err")
            return redirect(url_for("admin.auth_edit", id=id))
        if (
            data["name"] != auth.name
            and Auth.query.filter_by(name=data["name"]).count() == 1
        ):
            flash('权限"{0}"已经存在!'.format(data["name"]), "err")
            return redirect(url_for("admin.auth_edit", id=id))
        oplog = OpLog(
            admin_id=session["admin_id"],
            ip=request.remote_addr,
            reason='修改权限"{0}"的信息'.format(auth.name),
        )
        auth.name = data["name"]
        auth.url = data["url"]
        db.session.add(auth)
        db.session.add(oplog)
        db.session.commit()
        flash("权限信息已修改!", "ok")
        return redirect(url_for("admin.auth_edit", id=id))
    return render_template("admin/auth_edit.html", form=form, auth=auth)


# 添加管理员
@admin.route("/admin/add/", methods=["GET", "POST"])
@admin_login_required
@admin_auth
def admin_add():
    form = AdminForm()
    if form.validate_on_submit():
        data = form.data
        if Admin.query.filter_by(name=data["name"]).count() == 1:
            flash('管理员"{0}"已经存在！'.format(data["name"]), "err")
            return redirect(url_for("admin.admin_add"))
        from werkzeug.security import generate_password_hash

        admin = Admin(
            name=data["name"],
            pwd=generate_password_hash(data["pwd"]),
            is_super=1,
            role_id=data["role_id"],
        )
        db.session.add(admin)
        oplog = OpLog(
            admin_id=session["admin_id"],
            ip=request.remote_addr,
            reason='添加管理员"{0}"'.format(data["name"]),
        )
        db.session.add(oplog)
        db.session.commit()
        flash('管理员"{0}"添加成功！'.format(data["name"]), "ok")
        return redirect(url_for("admin.admin_add"))
    return render_template("admin/admin_add.html", form=form)


# 管理员列表
@admin.route("/admin/list/<int:page>/", methods=["GET"])
@admin_login_required
@admin_auth
def admin_list(page=None):
    if page is None:
        page = 1
    page_data = (
        Admin.query.join(Role)
        .filter(Role.id == Admin.role_id)
        .order_by(Admin.add_time.desc())
        .paginate(page=page, per_page=10)
    )
    return render_template("admin/admin_list.html", page_data=page_data)


# TODO:管理员修改与删除
