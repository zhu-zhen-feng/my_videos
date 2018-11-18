from flask import abort, jsonify, redirect
from flask import current_app
from flask import g
from flask import request

from info import db
from info.models import Videos, Comment
from info.modules.videos import videos_blu
from flask import render_template

from info.utils.common import user_login_data
from info.utils.response_code import RET


@videos_blu.route('/video_comment', methods=["POST"])
@user_login_data
def comment_video():
    """
    评论新闻或者回复某条新闻下指定的评论
    :return:
    """

    user = g.user
    if not user:
        return jsonify(errno=RET.SESSIONERR, errmsg="用户未登录")

    # 1. 取到请求参数
    video_id = request.json.get("video_id")
    comment_content = request.json.get("comment")
    parent_id = request.json.get("parent_id")

    # 2. 判断参数
    if not all([video_id, comment_content]):
        return jsonify(errno=RET.PARAMERR, errmsg="参数错误")

    try:
        video_id = int(video_id)
        if parent_id:
            parent_id = int(parent_id)
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.PARAMERR, errmsg="参数错误")

    # 查询并判断视频是否存在
    try:
        video = Videos.query.get(video_id)
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.DBERR, errmsg="数据查询错误")

    if not video:
        return jsonify(errno=RET.NODATA, errmsg="未查询到新闻数据")

    # 3. 初始化一个评论模型，并且赋值
    comment = Comment()
    comment.user_id = user.id
    comment.class_id = video_id
    comment.content = comment_content
    if parent_id:
        comment.parent_id = parent_id

    # 添加到数据库
    # 为什么要自己去commit()?，因为在return的时候需要用到 comment 的 id
    try:
        db.session.add(comment)
        db.session.commit()
    except Exception as e:
        current_app.logger.error(e)
        db.session.rollback()

    return jsonify(errno=RET.OK, errmsg="OK", data=comment.to_dict())


@videos_blu.route('/video_collect', methods=["POST"])
@user_login_data
def collect_video():
    """
    视频收藏
    1. 接受参数
    2. 判断参数
    3. 查询视频，并判断视频是否存在
    :return:
    """

    user = g.user
    if not user:
        return jsonify(errno=RET.SESSIONERR, errmsg="用户未登录")

    # 1. 接受参数
    video_id = request.json.get("video_id")
    action = request.json.get("action")

    # 2. 判断参数
    if not all([video_id, action]):
        return jsonify(errno=RET.PARAMERR, errmsg="参数错误")

    if action not in ["collect", "cancel_collect"]:
        return jsonify(errno=RET.PARAMERR, errmsg="参数错误")

    try:
        video_id = int(video_id)
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.PARAMERR, errmsg="参数错误")

    # 3. 查询新闻，并判断新闻是否存在
    try:
        video = Videos.query.get(video_id)
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.DBERR, errmsg="数据查询错误")

    if not video:
        return jsonify(errno=RET.NODATA, errmsg="未查询到新闻数据")

    # 4. 收藏以及取消收藏
    if action == "cancel_collect":
        # 取消收藏
        if video in user.collection_videos:
            user.collection_videos.remove(video)
    else:
        # 收藏
        if video not in user.collection_videos:
            # 添加到用户的新闻收藏列表
            user.collection_videos.append(video)

    return jsonify(errno=RET.OK, errmsg="操作成功")


@videos_blu.route('/<int:video_id>')
@user_login_data
def news_detail(video_id):
    """
    视频详情
    :param video_id:
    :return:
    """

    # 查询用户登录信息
    user = g.user
    if not user:
        # 代表没有登录，重定向到首页
        return redirect("/")

    # 查询新闻数据
    videos = None

    try:
        videos = Videos.query.get(video_id)
    except Exception as e:
        current_app.logger.error(e)

    if not videos:
        # 报404错误，404错误统一显示页面后续再处理
        abort(404)

    # 更新新闻的点击次数
    videos.clicks += 1

    # 是否是收藏　
    is_collected = False

    # if 用户已登录：
    #     判断用户是否收藏当前新闻，如果收藏：
    #         is_collected = True

    if user:
        # 判断用户是否收藏当前新闻，如果收藏：
        # collection_news 后面可以不用加all，因为sqlalchemy会在使用的时候去自动加载
        if videos in user.collection_videos:
            is_collected = True

    # 去查询评论数据
    comments = []
    try:
        comments = Comment.query.filter(Comment.class_id == video_id).order_by(Comment.create_time.desc()).all()
    except Exception as e:
        current_app.logger.error(e)
    comment_list = []
    for comment in comments:
        comment_list.append(comment.to_dict())

    data = {
        "user": user.to_dict() if user else None,
        "video": videos.to_dict(),
        "comments": comment_list,
        "is_collected": is_collected,
    }

    return render_template("videos/play.html", data=data)
