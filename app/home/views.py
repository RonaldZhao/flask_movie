# 视图处理文件
import os
import stat
import uuid
from datetime import datetime
from functools import wraps

from flask import render_template, redirect, url_for, flash, session, request
from werkzeug.security import generate_password_hash
from werkzeug.utils import secure_filename

from . import home
from app.home.forms import RegisterForm, LoginForm, UserDetailForm, PwdForm
from app.models import User, UserLog
from app import db, app


def user_login_required(func):
    @wraps(func)
    def deco(*args, **kwargs):
        if "user" not in session:
            return redirect(url_for("home.login", next=request.url))
        return func(*args, **kwargs)

    return deco


def change_filename(file_name):
    file_info = os.path.splitext(file_name)
    file_name = (
        datetime.now().strftime("%Y%m%d%H%M%S")
        + str(uuid.uuid4().hex)
        + file_info[-1]
    )
    return file_name


@home.route("/")
def index():
    return render_template("home/index.html")


@home.route("/login/", methods=["GET", "POST"])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        data = form.data
        user = User.query.filter_by(email=data["email"]).first()
        if not user.check_pwd(data["pwd"]):
            flash("密码错误！", "err")
            return redirect(url_for("home.login"))
        session["user"] = user.email
        userlog = UserLog(user_id=user.id, ip=request.remote_addr)
        db.session.add(userlog)
        db.session.commit()
        return redirect(request.args.get("next") or url_for("home.index"))
    return render_template("home/login.html", form=form)


@home.route("/logout/")
@user_login_required
def logout():
    session.pop("user", None)
    return redirect(url_for("home.login"))


@home.route("/register/", methods=["GET", "POST"])
def register():
    form = RegisterForm()
    if form.validate_on_submit():
        data = form.data
        user = User(
            name=data["name"],
            pwd=generate_password_hash(data["pwd"]),
            email=data["email"],
            phone=data["phone"],
            info="",
            face="",
            uuid=uuid.uuid4().hex,
        )
        db.session.add(user)
        db.session.commit()
        flash("注册成功!", "ok")
        return redirect(url_for("home.login"))
    return render_template("home/register.html", form=form)


@home.route("/user/", methods=["GET", "POST"])
@user_login_required
def user():
    form = UserDetailForm()
    form.face.validators.clear()
    user = User.query.filter_by(email=session["user"]).first()
    if request.method == "GET":
        form.name.data = user.name
        form.email.data = user.email
        form.phone.data = user.phone
        form.info.data = user.info
    if form.validate_on_submit():
        data = form.data
        changed = False
        if data["name"] != user.name:
            user.name = data["name"]
            changed = True
        if data["email"] != user.email:
            user.email = data["email"]
            changed = True
        if data["phone"] != user.phone:
            user.phone = data["phone"]
            changed = True
        if type(form.face.data) != str and form.face.data.filename != "":
            if not os.path.exists(app.config["FACE_DIR"]):
                os.makedirs(app.config["FACE_DIR"])
                os.chmod(app.config["FACE_DIR"], stat.S_IRWXU)
            if user.face != "" and os.path.exists(
                app.config["FACE_DIR"] + user.face
            ):
                os.remove(app.config["FACE_DIR"] + user.face)
            file_face = secure_filename(form.face.data.filename)
            user.face = change_filename(file_face)
            form.face.data.save(app.config["FACE_DIR"] + user.face)
            changed = True
        if data["info"] != user.info:
            user.info = data["info"]
            changed = True
        if not changed:
            flash("不作修改则不需要保存的哟~~~", "err")
        else:
            flash("修改信息成功！", "ok")
            db.session.add(user)
            db.session.commit()
        return redirect(url_for("home.user"))
    return render_template("home/user.html", form=form, user=user)


@home.route("/pwd/", methods=["GET", "POST"])
@user_login_required
def pwd():
    form = PwdForm()
    if form.validate_on_submit():
        data = form.data
        user = User.query.filter_by(email=session["user"]).first()
        if not user.check_pwd(data["old_pwd"]):
            flash("当前密码输入错误！", "err")
            return redirect(url_for("home.pwd"))
        user.pwd = generate_password_hash(data["new_pwd"])
        db.session.add(user)
        db.session.commit()
        flash("密码修改成功！请重新登录", "ok")
        return redirect(url_for("home.logout"))
    return render_template("home/pwd.html", form=form)


@home.route("/comments/")
@user_login_required
def comments():
    return render_template("home/comments.html")


@home.route("/loginlog/list/<int:page>/", methods=["GET"])
@user_login_required
def loginlog(page=None):
    if page is None:
        page = 1
    page_data = (
        UserLog.query.join(User)
        .filter(UserLog.user_id == User.id)
        .order_by(UserLog.login_time.desc())
        .paginate(page=page, per_page=10)
    )
    return render_template("home/loginlog.html", page_data=page_data)


@home.route("/moviecol/")
@user_login_required
def moviecol():
    return render_template("home/moviecol.html")


@home.route("/animation/")
def animation():
    return render_template("home/animation.html")


@home.route("/search/")
def search():
    return render_template("home/search.html")


@home.route("/play/")
def play():
    return render_template("home/play.html")
