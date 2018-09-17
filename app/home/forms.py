# 表单处理文件
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField
from wtforms.validators import (
    DataRequired,
    EqualTo,
    Email,
    Regexp,
    ValidationError,
)

from app.models import User


class RegisterForm(FlaskForm):
    name = StringField(
        label="昵称",
        validators=[DataRequired("请输入昵称!")],
        description="昵称",
        render_kw={"class": "form-control input-lg", "placeholder": "请输入昵称"},
    )
    email = StringField(
        label="邮箱",
        validators=[DataRequired("请输入邮箱!"), Email("邮箱格式不正确")],
        description="邮箱",
        render_kw={"class": "form-control input-lg", "placeholder": "请输入邮箱"},
    )
    phone = StringField(
        label="手机号",
        validators=[
            DataRequired("请输入手机号!"),
            Regexp("^1[34578]\d{9}$", message="手机号格式不正确!"),
        ],
        description="手机号",
        render_kw={"class": "form-control input-lg", "placeholder": "请输入手机号"},
    )
    pwd = PasswordField(
        label="密码",
        validators=[DataRequired("请输入密码!")],
        description="密码",
        render_kw={"class": "form-control input-lg", "placeholder": "请输入密码"},
    )
    pwd2 = PasswordField(
        label="确认密码",
        validators=[
            DataRequired("请输入确认密码!"),
            EqualTo("pwd", message="两次密码输入不一致!"),
        ],
        description="确认密码",
        render_kw={"class": "form-control input-lg", "placeholder": "请输入确认密码"},
    )
    submit = SubmitField(
        label="注册", render_kw={"class": "btn btn-lg btn-success btn-block"}
    )

    def validate_name(self, field):
        if User.query.filter_by(name=field.data).count() == 1:
            raise ValidationError("此昵称已存在!")

    def validate_email(self, field):
        if User.query.filter_by(email=field.data).count() == 1:
            raise ValidationError("此邮箱已注册!")

    def validate_phone(self, field):
        if User.query.filter_by(phone=field.data).count() == 1:
            raise ValidationError("此手机号已存在!")


class LoginForm(FlaskForm):
    email = StringField(
        label="邮箱",
        validators=[DataRequired("请输入邮箱!"), Email("邮箱格式不正确")],
        description="邮箱",
        render_kw={"class": "form-control input-lg", "placeholder": "邮箱"},
    )
    pwd = PasswordField(
        label="密码",
        validators=[DataRequired("请输入密码!")],
        description="密码",
        render_kw={"class": "form-control input-lg", "placeholder": "密码"},
    )
    submit = SubmitField(
        label="登录", render_kw={"class": "btn btn-lg btn-success btn-block"}
    )

    def validate_email(self, field):
        email = field.data
        user = User.query.filter_by(email=email).count()
        if user != 1:
            raise ValidationError("此邮箱暂未注册！")
