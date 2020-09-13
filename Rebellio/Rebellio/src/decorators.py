import hashlib
from functools import wraps
from django.shortcuts import redirect


def is_login_decorator(func):
    """
    判断用户是否登录
    """
    @wraps(func)
    def wrapped_function(request):
        if not request.session.get('is_login', None):
            return redirect('/login')
        if request.session.get('user_name', '') == '':
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
        if user_access_level < 1:
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
        if user_access_level < 3:
            return redirect('/home')
        return func(request)

    return wrapped_function
