from django.http import HttpResponse
from . import settings
from django.shortcuts import render,redirect
from django.views.decorators.http import require_http_methods
from django.db.models import Q
from . import models
from . import forms
from .src import fumen
from .src import account
from .src import utils
import math


def test(request):
    return HttpResponse(settings.STATICFILES_DIRS)

def home(request):
    return render(request, 'home.html')

# 登陆登出操作
@require_http_methods(['GET','POST'])
def login(request):
    if request.session.get('is_login',None):
        return redirect('/home')

    if request.method == "POST":
        login_form = forms.UserForm(request.POST)
        message = "请检查填写的内容！"
        if login_form.is_valid():
            username = login_form.cleaned_data['username']
            password = login_form.cleaned_data['password']
            try:
                user = models.Accounts.objects.get(Q(accountname=username))
                if password == user.passwd:
                    request.session['is_login'] = True
                    request.session['user_name'] = user.accountname
                    request.session['user_access_level'] = user.accesslevel
                    return redirect('/home')
                else:
                    message = "密码不正确！"
            except Exception as e:
                message = "用户不存在！"
        return render(request, 'login/login.html', locals())

    login_form = forms.UserForm()
    return render(request, 'login/login.html', locals())

@require_http_methods(['GET','POST'])
def logout(request):
    if not request.session.get('is_login', None):
        return redirect("/home")
    request.session.flush()
    return redirect("/home")

# 谱面操作
@require_http_methods(['GET'])
def get_fumens(request):
    if not request.session.get('is_login', None):
        return redirect('/login')
        
    keyword = request.GET.get('keyword', '')
    fumen_creator = request.GET.get('fumen_creator', '')
    category = request.GET.get('category', 0)
    start_page = int(request.GET.get('start_page', 1))
    page_size = int(request.GET.get('page_size', 10))
    level = int(request.GET.get('level', 0))
    user_access_level = request.session.get('user_access_level', 0)

    fumens, total, total_page, pages, start_page = fumen.get_fumens(keyword, fumen_creator, category, start_page, page_size, level, user_access_level, '')
    result = {'data': fumens, 'total': total}
    fumen.set_return_result(result, 'fumen', keyword, fumen_creator, category, start_page, page_size, total_page, pages, level)
    return render(request, 'fumen/fumen.html', result)

@require_http_methods(['GET'])
def get_own_fumens(request):
    if not request.session.get('is_login', None):
        return redirect('/login')
        
    keyword = request.GET.get('keyword', '')
    fumen_creator = request.GET.get('fumen_creator', '')
    category = request.GET.get('category', 0)
    start_page = int(request.GET.get('start_page', 1))
    page_size = int(request.GET.get('page_size', 10))
    level = int(request.GET.get('level', 0))
    user_access_level = request.session.get('user_access_level', 0)
    user_name = request.session.get('user_name', '')

    fumens, total, total_page, pages, start_page = fumen.get_fumens(keyword, fumen_creator, category, start_page, page_size, level, user_access_level, user_name)
    result = {'data': fumens, 'total': total}
    fumen.set_return_result(result, 'own_fumen', keyword, fumen_creator, category, start_page, page_size, total_page, pages, level)
    return render(request, 'fumen/own_fumen.html', result)

@require_http_methods(['GET'])
def get_fumen(request):
    if not request.session.get('is_login', None):
        return redirect('/login')

    fumen_id = int(request.GET.get('fumen_id', 0))
    is_show_all_records = int(request.GET.get('is_show_all_records', 0))
    is_show_all_comments = int(request.GET.get('is_show_all_comments', 0))
    user_access_level = request.session.get('user_access_level', 0)
    user_name = request.session.get('user_name', '')

    fumen_detail = fumen.get_fumen(fumen_id, user_access_level)
    if fumen_detail is None:
        return redirect('/fumen')
    best_record, player_records = account.get_fumen_record(user_name, fumen_id, is_show_all_records)
    comments = account.get_fumen_comments(fumen_id, is_show_all_comments)
    return render(request, 'fumen/fumen_detail.html', {'data':fumen_detail, 'total':1, 'best_record':best_record, 'player_records':player_records, 'comments':comments})

@require_http_methods(['GET'])
def comment_on_fumen(request):
    if not request.session.get('is_login', None):
        return redirect('/login')

    fumen_id = int(request.GET.get('fumen_id', 0))
    comment = request.GET.get('comment', 0)
    user_access_level = request.session.get('user_access_level', 0)
    user_name = request.session.get('user_name', '')

    result = account.comment_on_fumen(fumen_id, user_name, user_access_level, comment)
    return redirect('/fumen/fumen_detail/?fumen_id={0}'.format(fumen_id))