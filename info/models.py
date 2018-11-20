from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash

from info import constants
from . import db


class BaseModel(object):
    """模型基类，为每个模型补充创建时间与更新时间"""
    create_time = db.Column(db.DateTime, default=datetime.now)  # 记录的创建时间


# 用户收藏表，建立用户与其收藏新闻多对多的关系
tb_user_collection = db.Table(
    "info_user_collection",
    db.Column("user_id", db.Integer, db.ForeignKey("user.id"), primary_key=True),  # 新闻编号
    db.Column("video_id", db.Integer, db.ForeignKey("videos.id"), primary_key=True),  # 分类编号
    db.Column("create_time", db.DateTime, default=datetime.now)  # 收藏创建时间
)


class User(BaseModel, db.Model):
    """用户"""
    __tablename__ = "user"

    id = db.Column(db.Integer, primary_key=True)  # 用户编号
    nick_name = db.Column(db.String(32), unique=True, nullable=False)  # 用户昵称
    mobile = db.Column(db.String(11), unique=True, nullable=False)  # 手机号
    password_hash = db.Column(db.String(128), nullable=False)  # 加密的密码
    email = db.Column(db.String(30), unique=True)  # 邮箱
    update_time = db.Column(db.DateTime, default=datetime.now, onupdate=datetime.now)
    is_admin = db.Column(db.Boolean, default=False)
    collection_videos = db.relationship("Videos", secondary=tb_user_collection, lazy="dynamic")  # 用户收藏的

    @property
    def password(self):
        raise AttributeError("当前属性不允许读取")

    @password.setter
    def password(self, value):
        # self.password_hash = 对value加密
        self.password_hash = generate_password_hash(value)

    def check_password(self, password):
        """校验密码"""
        return check_password_hash(self.password_hash, password)

    def to_dict(self):
        resp_dict = {
            "id": self.id,
            "nick_name": self.nick_name,
            "mobile": self.mobile,
            "is_admin":self.is_admin,
            "register": self.create_time.strftime("%Y-%m-%d %H:%M:%S"),
            "last_login": self.update_time.strftime("%Y-%m-%d %H:%M:%S"),
        }
        return resp_dict


class Comment(BaseModel, db.Model):
    """评论"""
    __tablename__ = "comment"

    id = db.Column(db.Integer, primary_key=True)  # 评论编号
    content = db.Column(db.Text, nullable=False)  # 评论内容
    parent_id = db.Column(db.Integer, db.ForeignKey("comment.id"))  # 父评论id
    parent = db.relationship("Comment", remote_side=[id])  # 自关联
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)  # 用户id
    class_id = db.Column(db.Integer, db.ForeignKey("videos.id"), nullable=False)  # 视频id

    def to_dict(self):
        resp_dict = {
            "id": self.id,
            "create_time": self.create_time.strftime("%Y-%m-%d %H:%M:%S"),
            "content": self.content,
            "parent": self.parent.to_dict() if self.parent else None,
            "user": User.query.get(self.user_id).to_dict(),
            "video_id": self.class_id
        }
        return resp_dict


class Subject(BaseModel, db.Model):
    """视频分类"""
    __tablename__ = "subject"

    id = db.Column(db.Integer, primary_key=True)  # 分类编号
    name = db.Column(db.String(64), nullable=False)  # 分类名
    cid = db.Column(db.Integer, db.ForeignKey("subject.id"))
    video_list = db.relationship('Videos', backref='subject', lazy='dynamic')

    def to_dict(self):
        resp_dict = {
            "id": self.id,
            "name": self.name,
            "cid":self.cid
        }
        return resp_dict


class Videos(BaseModel, db.Model):
    """视频表"""
    __tablename__ = "videos"

    id = db.Column(db.Integer, primary_key=True)
    intro = db.Column(db.String(60), nullable=False)  # 简介
    url = db.Column(db.String(256))  # 视频地址
    clicks = db.Column(db.Integer, default=0)  # 播放次数
    subject_id = db.Column(db.Integer, db.ForeignKey("subject.id"), nullable=False)  # 分类id

    def to_dict(self):
        rep_dict = {
            "id": self.id,
            "intro": self.intro,
            "url": self.url,
            "clicks": self.clicks,
            "subject": Subject.query.get(self.subject_id).to_dict(),
            "create_time": self.create_time
        }
        return rep_dict


class Collection(BaseModel, db.Model):
    """用户收藏视频的表"""
    __tablename__ = "collection"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)
    video_id = db.Column(db.Integer, db.ForeignKey("videos.id"), nullable=False)
