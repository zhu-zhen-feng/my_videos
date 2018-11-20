import functools
# 共用的自定义工具类
from flask import current_app
from flask import g
from flask import session
from info.models import User


def user_login_data(f):
    # 使用 functools.wraps 去装饰内层函数，可以保持当前装饰器去装饰的函数的 __name__ 的值不变
    @functools.wraps(f)
    def wrapper(*args, **kwargs):
        user_id = session.get("user_id", None)
        user = None
        if user_id:
            # 尝试查询用户的模型
            try:
                user = User.query.get(user_id)
            except Exception as e:
                current_app.logger.error(e)
        # 把查询出来的数据赋值给g变量
        g.user = user
        return f(*args, **kwargs)
    return wrapper

