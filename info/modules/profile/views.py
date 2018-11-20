import datetime
import os
import uuid
from flask import g
from flask import redirect, jsonify
from flask import render_template
from flask import request
from werkzeug.utils import secure_filename
from config import Config
from info.models import Videos, Subject
from info.modules.profile import profile_blu
from info.utils.common import user_login_data
from info.utils.response_code import RET
from flask_wtf import FlaskForm
from wtforms import StringField, FileField, SubmitField, SelectField
from wtforms.validators import DataRequired
from flask import current_app, flash, url_for
from info import constants, db, create_app

with create_app().app_context():  # 解决RuntimeError: application not registered on db instance and
    tags = Subject.query.filter(Subject.cid == None)


class MovieForm(FlaskForm):
    """
    电影表单
    """
    subject_id = SelectField(
        label="分类 ：",
        validators=[
            DataRequired("请选择分类！")
        ],
        coerce=int,
        choices=[(v.id, v.name) for v in tags],
        description="分类",
        render_kw={
            "class": "sel_opt",
            "id": "input_tag_id"
        }
    )
    title = StringField(
        label="简介 ：",
        validators=[
            DataRequired("请输入简介！")
        ],
        description="简介",
        render_kw={
            "class": "input_txt2",
            "id": "input_title",
            "placeholder": "请输入简介！"
        }
    )
    url = FileField(
        label="文件 ：",
        validators=[
            DataRequired("请上传视频！")
        ],
        description="文件",
    )
    submit = SubmitField(
        label="编辑",
        render_kw={
            "class": "input_sub input_sub2",
        }
    )


def change_filename(filename):
    fileinfo = os.path.splitext(filename)
    filename = datetime.datetime.now().strftime("%Y%m%d%H%M%S") + str(uuid.uuid4().hex) + fileinfo[-1]
    return filename


@profile_blu.route('/video_list')
@user_login_data
def user_video_list():
    # 获取参数
    page = request.args.get("p", 1)

    # 判断参数
    try:
        page = int(page)
    except Exception as e:
        current_app.logger.error(e)
        page = 1

    user = g.user
    video_list = []
    current_page = 1
    total_page = 1
    try:
        paginate = Videos.query.paginate(page, constants.USER_COLLECTION_MAX_NEWS,
                                         False)
        video_list = paginate.items
        current_page = paginate.page
        total_page = paginate.pages
    except Exception as e:
        current_app.logger.error(e)

    video_dict_li = []
    for video in video_list:
        video_dict_li.append(video.to_dict())

    data = {
        "video_dict": video_dict_li,
        "total_page": total_page,
        "current_page": current_page,
    }

    return render_template('videos/user_video_list.html', data=data)


@profile_blu.route('/collection')
@user_login_data
def user_collection():
    # 获取参数
    page = request.args.get("p", 1)

    # 判断参数
    try:
        page = int(page)
    except Exception as e:
        current_app.logger.error(e)
        page = 1

    # 查询用户指定页数的收藏的视频
    user = g.user

    video_list = []
    total_page = 1
    current_page = 1
    try:
        paginate = user.collection_videos.paginate(page, constants.USER_COLLECTION_MAX_NEWS, False)
        current_page = paginate.page
        total_page = paginate.pages
        video_list = paginate.items
    except Exception as e:
        current_app.logger.error(e)

    video_dict_li = []
    for video in video_list:
        video_dict_li.append(video.to_dict())

    data = {
        "total_page": total_page,
        "current_page": current_page,
        "collections": video_dict_li
    }

    return render_template('videos/user_collection.html', data=data)


@profile_blu.route('/pass_info', methods=["GET", "POST"])
@user_login_data
def pass_info():
    if request.method == "GET":
        return render_template('videos/user_pass_info.html')

    # 1. 获取参数
    old_password = request.json.get("old_password")
    news_password = request.json.get("new_password")

    # 2. 校验参数
    if not all([old_password, news_password]):
        return jsonify(errno=RET.PARAMERR, errmsg="参数错误")

    # 3. 判断旧密码是否正确
    user = g.user
    if not user.check_password(old_password):
        return jsonify(errno=RET.PWDERR, errmsg="原密码错误")

    # 4. 设置新密码
    user.password = news_password

    return jsonify(errno=RET.OK, errmsg="保存成功")


@profile_blu.route('/info')
@user_login_data
def user_info():
    user = g.user
    if not user:
        # 代表没有登录，重定向到首页
        return redirect("/")
    data = {"user": user.to_dict()}
    return render_template('videos/user.html', data=data)


@profile_blu.route('/video_release', methods=["get", "post"])
@user_login_data
def video_add():
    form = MovieForm()
    if form.validate_on_submit():
        data = form.data
        file_url = secure_filename(form.url.data.filename)
        if not os.path.exists(Config.UP_DIR):
            os.makedirs(Config.UP_DIR)
            os.chmod(Config.UP_DIR, "rw")
        url = change_filename(file_url)
        form.url.data.save(Config.UP_DIR + url)
        movie = Videos()
        movie.intro = data["title"],
        movie.url = url,
        movie.clicks = 0,
        movie.subject_id = int(data["subject_id"])
        try:
            db.session.add(movie)
        except Exception as e:
            flash("添加视频失败！", "error")
            db.session.rollback()
        db.session.commit()
        return redirect(url_for('profile.video_add'))
    return render_template("videos/user_video_release.html", form=form)
