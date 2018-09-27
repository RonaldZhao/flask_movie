# 表单处理文件
from flask_wtf import FlaskForm
from wtforms import (
    StringField,
    PasswordField,
    SubmitField,
    FileField,
    TextAreaField,
    SelectField,
    SelectMultipleField,
)
from wtforms.validators import DataRequired, ValidationError, EqualTo

from app.models import Admin, Tag, Auth, Role

auth_list = Auth.query.all()
role_list = Role.query.all()


class LoginForm(FlaskForm):
    """
    管理员登录表单
    """

    account = StringField(
        label="账号",
        validators=[DataRequired("请输入账号!")],
        description="账号",
        render_kw={
            "class": "form-control",
            "placeholder": "请输入账号",
            "required": "required",
        },
    )
    pwd = PasswordField(
        label="密码",
        validators=[DataRequired("请输入密码!")],
        description="密码",
        render_kw={
            "class": "form-control",
            "placeholder": "请输入密码",
            "required": "required",
        },
    )
    submit = SubmitField(
        label="登录", render_kw={"class": "btn btn-primary btn-block btn-flat"}
    )

    def validate_account(self, field):
        account = field.data
        admin = Admin.query.filter_by(name=account).count()
        if admin == 0:
            raise ValidationError("账号不存在!")


class TagForm(FlaskForm):
    name = StringField(
        label="名称",
        validators=[DataRequired("请输入标签!")],
        description="标签",
        render_kw={
            "class": "form-control",
            "id": "input_name",
            "placeholder": "请输入标签名称",
        },
    )
    submit = SubmitField(label="添加", render_kw={"class": "btn btn-primary"})


class MovieForm(FlaskForm):
    title = StringField(
        label="影片名称",
        validators=[DataRequired("请输入影片名称!")],
        description="影片名称",
        render_kw={"class": "form-control", "placeholder": "请输入影片名称"},
    )
    url = FileField(
        label="文件", validators=[DataRequired("请选择影片文件!")], description="影片文件"
    )
    info = TextAreaField(
        label="影片简介",
        validators=[DataRequired("请输入影片简介!")],
        description="影片简介",
        render_kw={"class": "form-control", "rows": 10},
    )
    logo = FileField(
        label="封面文件", validators=[DataRequired("请选择封面文件!")], description="封面文件"
    )
    star = SelectField(
        label="星级",
        validators=[DataRequired("请选择星级!")],
        coerce=int,
        choices=[(1, "1星"), (2, "2星"), (3, "3星"), (4, "4星"), (5, "5星")],
        description="影片星级",
        render_kw={"class": "form-control"},
    )
    # TODO: 改为多选
    tag_id = SelectField(
        label="标签",
        validators=[DataRequired("请选择标签!")],
        coerce=int,
        choices=[(v.id, v.name) for v in Tag.query.all()],
        description="影片标签",
        render_kw={"class": "form-control"},
    )
    area = StringField(
        label="影片地区",
        validators=[DataRequired("请输入影片地区!")],
        description="影片地区",
        render_kw={"class": "form-control", "placeholder": "请输入影片地区"},
    )
    length = StringField(
        label="影片时长",
        validators=[DataRequired("请输入影片时长!")],
        description="影片时长",
        render_kw={"class": "form-control", "placeholder": "请输入影片时长"},
    )
    release_time = StringField(
        label="影片上映时间",
        validators=[DataRequired("请选择影片上映时间!")],
        description="影片上映时间",
        render_kw={
            "class": "form-control",
            "id": "input_release_time",
            "placeholder": "请选择影片上映时间",
        },
    )
    submit = SubmitField(label="添加", render_kw={"class": "btn btn-primary"})


class PreviewForm(FlaskForm):
    title = StringField(
        label="影片名称",
        validators=[DataRequired("请输入影片名称!")],
        description="影片名称",
        render_kw={"class": "form-control", "placeholder": "请输入影片名称"},
    )
    logo = FileField(
        label="文件",
        validators=[DataRequired("请选择影片封面图文件!")],
        description="影片封面图文件",
    )
    submit = SubmitField(label="添加", render_kw={"class": "btn btn-primary"})


class PwdForm(FlaskForm):
    old_pwd = PasswordField(
        label="当前密码",
        validators=[DataRequired("请输入当前密码!")],
        description="当前密码",
        render_kw={"class": "form-control", "placeholder": "请输入当前密码"},
    )
    new_pwd = PasswordField(
        label="新密码",
        validators=[DataRequired("请输入新密码!")],
        description="新密码",
        render_kw={"class": "form-control", "placeholder": "请输入新密码"},
    )
    submit = SubmitField(label="保存修改", render_kw={"class": "btn btn-primary"})

    def validate_old_pwd(self, field):
        from flask import session

        old_pwd = field.data
        name = session["admin"]
        admin = Admin.query.filter_by(name=name).first()
        if not admin.check_pwd(old_pwd):
            raise ValidationError("当前密码输入不正确!")


class AuthForm(FlaskForm):
    name = StringField(
        label="权限名称",
        validators=[DataRequired("请输入权限名称！")],
        description="权限名称",
        render_kw={"class": "form-control", "placeholder": "权限名称"},
    )
    url = StringField(
        label="权限地址",
        validators=[DataRequired("请输入权限地址！")],
        description="权限地址",
        render_kw={"class": "form-control", "placeholder": "权限地址"},
    )
    submit = SubmitField(label="添加", render_kw={"class": "btn btn-primary"})


class RoleForm(FlaskForm):
    name = StringField(
        label="角色名称",
        validators=[DataRequired("请输入角色名称！")],
        description="角色名称",
        render_kw={"class": "form-control"},
    )
    auths = SelectMultipleField(
        label="权限列表(按住Ctrl进行多选)",
        validators=[DataRequired("请至少选择一项")],
        coerce=int,
        choices=[(auth.id, auth.name) for auth in auth_list],
        description="权限列表",
        render_kw={"class": "form-control"},
    )
    submit = SubmitField(label="添加", render_kw={"class": "btn btn-primary"})


class AdminForm(FlaskForm):
    name = StringField(
        label="管理员名称",
        validators=[DataRequired("请输入管理员名称！")],
        description="管理员名称",
        render_kw={"class": "form-control", "placeholder": "管理员名称"},
    )
    pwd = PasswordField(
        label="密码",
        validators=[DataRequired("请输入管理员密码！")],
        description="管理员密码",
        render_kw={"class": "form-control", "placeholder": "管理员密码"},
    )
    pwd2 = PasswordField(
        label="重复管理员密码",
        validators=[
            DataRequired("请再次输入管理员密码"),
            EqualTo("pwd", message="两次密码输入不一致"),
        ],
        description="重复管理员密码",
        render_kw={"class": "form-control", "placeholder": "重复管理员密码"},
    )
    role_id = SelectField(
        label="请选择管理员角色",
        validators=[DataRequired("请选择管理员角色！")],
        coerce=int,
        choices=[(role.id, role.name) for role in role_list],
        render_kw={"class": "form-control"},
    )
    submit = SubmitField(label="添加", render_kw={"class": "btn btn-primary"})
