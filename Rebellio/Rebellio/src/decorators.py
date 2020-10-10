import logging
from functools import wraps
from django.shortcuts import redirect


logger = logging.getLogger(__name__)


def is_login_decorator(func):
    """
    判断用户是否登录
    """
    @wraps(func)
    def wrapped_function(request):
        if not request.session.get('is_login', None):
            logger.info("not login user, won't call function %s", func.__name__)
            return redirect('/login')
        if request.session.get('user_name', '') == '':
            logger.info("empty user name, won't call function %s", func.__name__)
            return redirect('/login')
        return func(request)

    return wrapped_function


def is_admin_decorator(func):
    """
    判断用户是否为管理员
    """
    @wraps(func)
    def wrapped_function(request):
        user_access_level = int(request.session.get('user_access_level', 0))
        user_name = request.session.get('user_name', '')
        if user_access_level < 1:
            logger.info("user %s is not admin, won't call function %s", user_name, func.__name__)
            return redirect('/home')
        return func(request)

    return wrapped_function


def is_super_admin_decorator(func):
    """
    判断用户是否为超级管理员
    """
    @wraps(func)
    def wrapped_function(request):
        user_access_level = int(request.session.get('user_access_level', 0))
        user_name = request.session.get('user_name', '')
        if user_access_level < 3:
            logger.info("user %s is not super admin, won't call function %s", user_name, func.__name__)
            return redirect('/home')
        return func(request)

    return wrapped_function
