from flask import current_app, jsonify, redirect
from flask import g
from flask import render_template
from flask import request
from info.models import Videos, Subject
from info.utils.common import user_login_data
from info.utils.response_code import RET
from . import index_blu


@index_blu.route('/video_list')
@user_login_data
def news_list():
    """
    获取首页数据
    :return:
    """
    # 1. 获取参数
    # 新闻的分类id

    cid = request.args.get("cid", "1")
    page = request.args.get("page", "1")
    per_page = request.args.get("per_page", "30")

    # 2. 校验参数
    try:
        page = int(page)
        cid = int(cid)
        per_page = int(per_page)
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.PARAMERR, errmsg="参数")

    # 查询当前cid的子目录
    subjects = []
    try:
        subjects = Videos.query.order_by(Videos.clicks.desc()).limit(6)
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.DBERR, errmsg="数据查询错误")
    subject_dict = []
    for subject in subjects:
        subject_dict.append(subject.to_dict())
    print(len(subject_dict))
    # 3. 查询数据
    try:
        paginate = Videos.query.filter(Videos.subject_id == cid).order_by(Videos.create_time.desc()).paginate(page, per_page, False)
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.DBERR, errmsg="数据查询错误")
    # 取到当前页的数据
    video_model_li = paginate.items  # 模型对象列表
    total_page = paginate.pages
    current_page = paginate.page

    # 将模型对象列表转成字典列表
    video_dict_li = []
    for video in video_model_li:
        video_dict_li.append(video.to_dict())
    data = {
        "total_page": total_page,
        "current_page": current_page,
        "video_dict_li": video_dict_li,
        "subject_dict":subject_dict,
    }
    return jsonify(errno=RET.OK, errmsg="OK", data=data)


@index_blu.route('/')
@user_login_data
def index():
    """
    显示首页
    1. 如果用户已经登录，将当前登录用户的数据传到模板中，供模板显示
    :return:
    """
    # 显示用户是否登录的逻辑
    # 取到用户id
    user = g.user
    # 查询左侧视频科目子目录
    subject_list = []
    try:
        subject_list = Subject.query.all()
    except Exception as e:
        current_app.logger.error(e)

    # 定义一个空的字典列表，里面装的就是字典
    subject_dict_li = []
    category_li = []
    # 遍历对象列表，将对象的字典添加到字典列表中
    for subject in subject_list:
        if subject.cid is None:
            category_li.append(subject.to_dict())
        else:
            subject_dict_li.append(subject.to_dict())
    data = {
        "user": user.to_dict() if user else None,
        "subject_dict": subject_dict_li,
        "category_li": category_li
    }

    return render_template('videos/index.html', data=data)


# 在打开网页的时候，浏览器会默认去请求根路径+favicon.ico作网站标签的小图标
# send_static_file 是 flask 去查找指定的静态文件所调用的方法
@index_blu.route('/favicon.ico')
def favicon():
    return current_app.send_static_file('videos/favicon.ico')


@index_blu.route('/search')
@user_login_data
def key_search():
    user = g.user
    keywords = request.args.get("keywords")
    if not keywords:
        return jsonify(errno=RET.PARAMERR, errmsg="参数错误")
        # 3. 查询数据
    try:
        video_list = Videos.query.filter(Videos.intro.contains(keywords)).order_by(Videos.create_time.desc())
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.DBERR, errmsg="数据查询错误")
    # 取到当前页的数据
    video_dict_li = []
    for video in video_list:
        video_dict_li.append(video.to_dict())
    data = {
        "user": user.to_dict() if user else None,
        "video_dict_li": video_dict_li,
    }

    return jsonify(errno=RET.OK, errmsg="OK", data=data)

