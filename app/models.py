# 数据模型文件
from datetime import datetime

from app import db

"""
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
import pymysql

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:123456@localhost/movie'  # 用于连接数据库
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = True  # 使Flask-SQLAlchemy追踪对象的修改并且发送信号
db = SQLAlchemy(app)
"""

# 会员数据模型
class User(db.Model):
    __tablename__ = 'user'
    id = db.Column(db.Integer, primary_key=True)  # 编号
    name = db.Column(db.String(100), unique=True)  # 昵称
    pwd = db.Column(db.String(100))  # 密码
    email = db.Column(db.String(100), unique=True)  # 邮箱
    phone = db.Column(db.String(11), unique=True)  # 手机号
    info = db.Column(db.Text)  # 简介
    face = db.Column(db.String(255))  # 头像(存储地址)
    register_time = db.Column(db.DateTime, index=True, default=datetime.now)  # 注册时间
    uuid = db.Column(db.String(255), unique=True)  # 唯一标识符
    comments = db.relationship('Comment', backref='user')  # 评论外键关联
    userlogs = db.relationship('UserLog', backref='user')  # 会员登录日志外键关联
    moviecols = db.relationship('Moviecol', backref='user')  # 电影收藏外键关联

    def check_pwd(self, pwd):
        from werkzeug.security import check_password_hash
        return check_password_hash(self.pwd, pwd)

    def __repr__(self):
        return '<User %r>' % self.name


# 会员登录日志数据模型
class UserLog(db.Model):
    __tablename__ = 'userlog'
    id = db.Column(db.Integer, primary_key=True)  # 编号
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))  # 所属会员
    ip = db.Column(db.String(100))  # 登录IP
    login_time = db.Column(db.DateTime, index=True, default=datetime.now)  # 登录时间

    def __repr__(self):
        return '<UserLog %r>' % self.id


# 标签数据模型
class Tag(db.Model):
    __tablename__ = 'tag'
    id = db.Column(db.Integer, primary_key=True)  # 编号
    name = db.Column(db.String(100))  # 标题
    add_time = db.Column(db.DateTime, index=True, default=datetime.now)  # 添加时间
    movies = db.relationship('Movie', backref='tag')  # 电影外键关联

    def __repr__(self):
        return '<Tag %r>' % self.name


# 电影数据模型
class Movie(db.Model):
    __tablename__ = 'movie'
    id = db.Column(db.Integer, primary_key=True)  # 编号
    title = db.Column(db.String(255), unique=True)  # 电影标题
    url = db.Column(db.String(255))  # 电影地址
    info = db.Column(db.Text)  # 电影简介
    logo = db.Column(db.String(255), unique=True)  # 电影封面
    star = db.Column(db.SmallInteger)  # 电影星级
    playnum = db.Column(db.BigInteger)  # 电影播放量
    commentnum = db.Column(db.BigInteger)  # 电影评论量
    area = db.Column(db.String(255))  # 上映地区
    release_time = db.Column(db.Date)  # 上映时间
    length = db.Column(db.String(100))  # 电影时长
    add_time = db.Column(db.DateTime, index=True, default=datetime.now)  # 添加时间
    tag_id = db.Column(db.Integer, db.ForeignKey('tag.id'))  # 所属标签
    comments = db.relationship('Comment', backref='movie')  # 电影评论外键关联
    moviecols = db.relationship('Moviecol', backref='movie')  # 电影收藏外键关联

    def __repr__(self):
        return '<Movie %r>' % self.title


# 上映预告数据模型
class Preview(db.Model):
    __tablename__ = 'preview'
    id = db.Column(db.Integer, primary_key=True)  # 编号
    title = db.Column(db.String(255), unique=True)  # 标题
    logo = db.Column(db.String(255), unique=True)  # 封面
    add_time = db.Column(db.DateTime, index=True, default=datetime.now)  # 添加时间

    def __repr__(self):
        return '<Preview %r>' % self.title


# 评论数据模型
class Comment(db.Model):
    __tablename__ = 'comment'
    id = db.Column(db.Integer, primary_key=True)  # 编号
    content = db.Column(db.Text)  # 评论内容
    movie_id = db.Column(db.Integer, db.ForeignKey('movie.id'))  # 所属电影
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))  # 所属用户
    add_time = db.Column(db.DateTime, index=True, default=datetime.now)  # 添加时间

    def __repr__(self):
        return '<Comment %r>' % self.id


# 收藏电影数据模型
class Moviecol(db.Model):
    __tablename__ = 'moviecol'
    id = db.Column(db.Integer, primary_key=True)  # 编号
    movie_id = db.Column(db.Integer, db.ForeignKey('movie.id'))  # 所属电影
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))  # 所属用户
    add_time = db.Column(db.DateTime, index=True, default=datetime.now)  # 添加时间

    def __repr__(self):
        return '<Moviecol %r>' % self.id


# 权限数据模型
class Auth(db.Model):
    __tablename__ = 'auth'
    id = db.Column(db.Integer, primary_key=True)  # 编号
    name = db.Column(db.String(100), unique=True)  # 名称
    url = db.Column(db.String(255), unique=True)  # 地址
    add_time = db.Column(db.DateTime, index=True, default=datetime.now)  # 添加时间

    def __repr__(self):
        return '<Auth %r>' % self.name


# 角色数据模型
class Role(db.Model):
    __tablename__ = 'role'
    id = db.Column(db.Integer, primary_key=True)  # 编号
    name = db.Column(db.String(100), unique=True)  # 名称
    auths = db.Column(db.String(600))  # 权限列表
    add_time = db.Column(db.DateTime, index=True, default=datetime.now)  # 添加时间
    admins = db.relationship('Admin', backref='role')  # 管理员外键关系关联

    def __repr__(self):
        return '<Role %r>' % self.name


# 管理员数据模型
class Admin(db.Model):
    __tablename__ = 'admin'
    id = db.Column(db.Integer, primary_key=True)  # 编号
    name = db.Column(db.String(100), unique=True)  # 管理员名称
    pwd = db.Column(db.String(100))  # 管理员密码
    is_super = db.Column(db.SmallInteger)  # 是否是超级管理员 o:是
    add_time = db.Column(db.DateTime, index=True, default=datetime.now)  # 添加时间
    role_id = db.Column(db.Integer, db.ForeignKey('role.id'))  # 角色编号
    admin_logs = db.relationship('AdminLog', backref='admin')  # 管理员登录日志外键关联
    oplogs = db.relationship('OpLog', backref='admin')  # 操作日志外键关联

    def check_pwd(self, pwd):
        from werkzeug.security import check_password_hash
        return check_password_hash(self.pwd, pwd)

    def __repr__(self):
        return '<Admin %r>' % self.name


# 管理员登录日志数据模型
class AdminLog(db.Model):
    __tablename__ = 'adminlog'
    id = db.Column(db.Integer, primary_key=True)  # 编号
    admin_id = db.Column(db.Integer, db.ForeignKey('admin.id'))  # 管理员所属编号
    ip = db.Column(db.String(100))  # 最近登录IP地址
    login_time = db.Column(db.DateTime, index=True, default=datetime.now)  # 登录时间

    def __repr__(self):
        return '<AdminLog %r>' % self.id


# 操作日志数据模型
class OpLog(db.Model):
    __tablename__ = 'oplog'
    id = db.Column(db.Integer, primary_key=True)  # 编号
    admin_id = db.Column(db.Integer, db.ForeignKey('admin.id'))  # 管理员所属编号
    ip = db.Column(db.String(100))  # 发送操作的IP地址
    reason = db.Column(db.String(600))  # 操作原因
    add_time = db.Column(db.DateTime, index=True, default=datetime.now)  # 发生时间

    def __repr__(self):
        return '<OpLog %r>' % self.id

"""
if __name__ == '__main__':
    db.create_all()

    role = Role(name='超级管理员', auths='')
    db.session.add(role)
    db.session.commit()

    from werkzeug.security import generate_password_hash
    admin = Admin(name='ronaldzhao', pwd=generate_password_hash('123456'), is_super=0, role_id=1)
    db.session.add(admin)
    db.session.commit()
"""
