# 视图处理文件
import uuid
from functools import wraps

from flask import render_template, redirect, url_for, flash, session, request
from werkzeug.security import generate_password_hash

from . import home
from app.home.forms import RegisterForm, LoginForm
from app.models import User
from app import db


def user_login_required(func):
    @wraps(func)
    def deco(*args, **kwargs):
        if "user" not in session:
            return redirect(url_for("home.login", next=request.url))
        return func(*args, **kwargs)

    return deco


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


@home.route("/user/")
@user_login_required
def user():
    return render_template("home/user.html")


@home.route("/pwd/")
@user_login_required
def pwd():
    return render_template("home/pwd.html")


@home.route("/comments/")
@user_login_required
def comments():
    return render_template("home/comments.html")


@home.route("/loginlog/")
@user_login_required
def loginlog():
    return render_template("home/loginlog.html")


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
