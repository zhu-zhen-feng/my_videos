from flask import current_app
from flask import g
from flask import redirect, jsonify
from flask import render_template
from flask import request

from info import constants, db
from info.models import Videos, Subject
from info.modules.profile import profile_blu
from info.utils.common import user_login_data
from info.utils.image_storage import storage
from info.utils.response_code import RET


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
        # paginate = Videos.query.filter(Videos.user_id == user.id).paginate(page, constants.USER_COLLECTION_MAX_NEWS,
        #                                                                    False)
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
def video_release():
    if request.method == "GET":
        # 加载分类数据
        categories = []
        try:
            categories = Subject.query.all()
        except Exception as e:
            current_app.logger.error(e)

        category_dict_li = []
        for category in categories:
            category_dict_li.append(category.to_dict())

        # 移除最新的分类
        category_dict_li.pop(0)

        return render_template('videos/user_video_release.html', data={"categories": category_dict_li})

    # 1. 获取要提交的数据
    # 标题
    about = request.form.get("about")
    # 视频
    file = request.files.get("video_file")
    img_url = request.files.get("index_image")
    # 分类id
    category_id = request.form.get("category_id")
    print([about, img_url, file, category_id])
    # 校验参数
    # 2.1 判断数据是否有值
    if not all([about, img_url, file, category_id]):
        return jsonify(errno=RET.PARAMERR, errmsg="参数有误")

    # 2.2
    try:
        category_id = int(category_id)
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.PARAMERR, errmsg="参数有误")
    # 3.取到图片，将图片上传到七牛云
    try:
        video = file.read()
        index_image_data = img_url.read()
        # 上传到七牛云
        url = storage(video)
        key = storage(index_image_data)
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.PARAMERR, errmsg="参数有误")

    if g.user.is_admin == False:
        # 1代表待审核状态
        video.status = 1
    else:
        video.status = 0
    video = Videos()
    video.intro = about
    video.img_url = constants.QINIU_DOMIN_PREFIX + key
    video.url = constants.QINIU_DOMIN_PREFIX + url
    video.category_id = category_id
    video.user_id = g.user.id

    try:
        db.session.add(video)
        db.session.commit()
    except Exception as e:
        current_app.logger.error(e)
        db.session.rollback()
        return jsonify(errno=RET.DBERR, errmsg="数据保存失败")

    return jsonify(errno=RET.OK, errmsg="OK")
