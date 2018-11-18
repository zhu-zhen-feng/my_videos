# 新闻详情模块的蓝图

from flask import Blueprint

# 创建蓝图对象
videos_blu = Blueprint("video", __name__, url_prefix="/videos")


from . import views