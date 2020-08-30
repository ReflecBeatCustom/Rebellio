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
from .src import inner
from .src import pack
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
                results = models.Accounts.objects.raw("SELECT * FROM Accounts WHERE AccountName = '{0}' AND Passwd = PASSWORD('{1}')".format(username, password))
                if len(results) > 0:
                    request.session['is_login'] = True
                    request.session['user_name'] = results[0].accountname
                    request.session['user_access_level'] = int(results[0].accesslevel)
                    return redirect('/home')
                else:
                    message = "密码不正确或用户不存在!"
            except Exception as e:
                message = "登陆失败,{0}".format(str(e))
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
    user_name = request.session.get('user_name', '')

    fumens, total, total_page, pages, start_page = fumen.get_fumens(keyword, fumen_creator, category, start_page, page_size, level, user_access_level, user_name, False)
    result = {'data': fumens, 'total': total}
    fumen.set_return_result(result, 'fumens', keyword, fumen_creator, category, start_page, page_size, total_page, pages, level)
    return render(request, 'fumen/fumens.html', result)

@require_http_methods(['GET'])
def get_unlocked_fumens(request):
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

    fumens, total, total_page, pages, start_page = fumen.get_unlocked_fumens(keyword, fumen_creator, category, start_page, page_size, level, user_access_level, user_name)
    result = {'data': fumens, 'total': total}
    fumen.set_return_result(result, 'unlock_fumens', keyword, fumen_creator, category, start_page, page_size, total_page, pages, level)
    return render(request, 'fumen/unlocked_fumen.html', result)

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

    fumens, total, total_page, pages, start_page = fumen.get_fumens(keyword, fumen_creator, category, start_page, page_size, level, user_access_level, user_name, True)
    result = {'data': fumens, 'total': total}
    fumen.set_return_result(result, 'own_fumens', keyword, fumen_creator, category, start_page, page_size, total_page, pages, level)
    return render(request, 'fumen/own_fumen.html', result)

@require_http_methods(['GET'])
def get_fumen(request):
    if not request.session.get('is_login', None):
        return redirect('/login')

    fumen_id = int(request.GET.get('fumen_id', 0))
    is_show_all_records = int(request.GET.get('is_show_all_records', 0))
    is_show_all_fumen_records = int(request.GET.get('is_show_all_fumen_records', 0))
    is_show_all_comments = int(request.GET.get('is_show_all_comments', 0))
    user_access_level = request.session.get('user_access_level', 0)
    user_name = request.session.get('user_name', '')

    fumen_detail = fumen.get_fumen(fumen_id, user_access_level)
    if fumen_detail is None:
        return redirect('/fumen')
    best_player_record, player_records = account.get_fumen_record(user_name, fumen_id, is_show_all_records)
    best_fumen_record, fumen_records = fumen.get_fumen_record(fumen_id, is_show_all_fumen_records)
    comments = account.get_fumen_comments(fumen_id, is_show_all_comments)
    return render(request, 'fumen/fumen_detail.html', {'data':fumen_detail, 'total':1, 'best_player_record':best_player_record, 'player_records':player_records, 'best_fumen_record':best_fumen_record, 'fumen_records':fumen_records, 'comments':comments})

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

# 曲包操作
@require_http_methods(['GET'])
def get_packs(request):
    if not request.session.get('is_login', None):
        return redirect('/login')
        
    keyword = request.GET.get('keyword', '')
    category = request.GET.get('category', 0)
    start_page = int(request.GET.get('start_page', 1))
    page_size = int(request.GET.get('page_size', 10))
    user_access_level = request.session.get('user_access_level', 0)

    packs, total, total_page, pages, start_page = pack.get_packs(user_access_level, start_page, page_size, keyword, category)
    result = {'data': packs}
    pack.set_return_result(result, 'packs', total, keyword, category, start_page, page_size, total_page, pages)
    return render(request, 'pack/packs.html', result)

@require_http_methods(['GET'])
def comment_on_pack(request):
    if not request.session.get('is_login', None):
        return redirect('/login')

    pack_id = int(request.GET.get('pack_id', 0))
    comment = request.GET.get('comment', 0)
    user_access_level = request.session.get('user_access_level', 0)
    user_name = request.session.get('user_name', '')

    result = account.comment_on_pack(pack_id, user_name, user_access_level, comment)
    return redirect('/pack/pack_detail?pack_id={0}'.format(pack_id))

@require_http_methods(['GET'])
def get_pack(request):
    if not request.session.get('is_login', None):
        return redirect('/login')
        
    pack_id = int(request.GET.get('pack_id', 10))
    user_access_level = request.session.get('user_access_level', 0)
    is_show_all_comments = int(request.GET.get('is_show_all_comments', 0))

    pack_detail = pack.get_pack(user_access_level, pack_id)
    comments = account.get_pack_comments(pack_id, is_show_all_comments)
    result = {'data': pack_detail ,'comments': comments}
    return render(request, 'pack/pack_detail.html', result)

# 内部功能
@require_http_methods(['GET'])
def inner_home(request):
    if not request.session.get('is_login', None):
        return redirect('/login')
    
    result = {'data': '这是内部主页'}
    return render(request, 'inner/inner_home.html', result)

@require_http_methods(['GET'])
def vote_on_subdiff(request):
    if not request.session.get('is_login', None):
        return redirect('/login')

    fumen_id = int(request.GET.get('fumen_id', 0))
    subdiff = int(request.GET.get('subdiff', 0))
    difficulty = int(request.GET.get('difficulty', 0))
    user_access_level = request.session.get('user_access_level', 0)
    user_name = request.session.get('user_name', '')

    result = inner.vote_on_subdiff(fumen_id, difficulty, user_name, user_access_level, subdiff)
    return redirect('/inner/subdiff_votes')

@require_http_methods(['GET'])
def get_subdiff_votes(request):
    if not request.session.get('is_login', None):
        return redirect('/login')

    user_access_level = request.session.get('user_access_level', 0)
    user_name = request.session.get('user_name', '')

    subdiff_votes = inner.get_subdiff_vote(user_name, user_access_level)
    result = {'subdiff_votes': subdiff_votes}
    inner.set_return_result(result, 'subdiff_vote')
    return render(request, 'inner/subdiff_votes.html', result)

@require_http_methods(['GET'])
def get_advice_fumens(request):
    if not request.session.get('is_login', None):
        return redirect('/login')

    user_access_level = request.session.get('user_access_level', 0)

    fumens = inner.get_advice_fumens(user_access_level)
    result = {'data': fumens}
    inner.set_return_result(result, 'advice_fumens')
    return render(request, 'inner/advice_fumens.html', result)

@require_http_methods(['GET'])
def super_manager(request):
    if not request.session.get('is_login', None):
        return redirect('/login')

    user_access_level = request.session.get('user_access_level', 0)
    if user_access_level < 3:
        return redirect('/home')
    
    need_vote_subdiff_fumen_diffs = inner.get_need_vote_subdiff_fumen_diffs(user_access_level)
    level1_admins, level2_admins, level3_admins = inner.get_admins(user_access_level)
    return render(request, 'inner/super_manager.html', {'need_vote_subdiff_fumen_diffs': need_vote_subdiff_fumen_diffs, 'level1_admins': level1_admins, 'level2_admins': level2_admins, 'level3_admins': level3_admins})

@require_http_methods(['GET'])
def add_subdiff_vote_fumen(request):
    if not request.session.get('is_login', None):
        return redirect('/login')

    user_access_level = request.session.get('user_access_level', 0)
    fumen_id = int(request.GET.get('fumen_id', 0))

    result = inner.add_subdiff_vote_fumen(user_access_level, fumen_id)
    return redirect('/inner/super_manager')

@require_http_methods(['GET'])
def delete_subdiff_vote_fumen(request):
    if not request.session.get('is_login', None):
        return redirect('/login')

    user_access_level = request.session.get('user_access_level', 0)
    fumen_id = int(request.GET.get('fumen_id', 0))

    result = inner.delete_subdiff_vote_fumen(user_access_level, fumen_id)
    return redirect('/inner/super_manager')

@require_http_methods(['GET'])
def update_packs(request):
    if not request.session.get('is_login', None):
        return redirect('/login')

    result = inner.update_packs(user_access_level)
    return redirect('/inner/super_manager')

@require_http_methods(['GET'])
def update_subdiffs(request):
    if not request.session.get('is_login', None):
        return redirect('/login')

    result = inner.update_subdiffs(user_access_level)
    return redirect('/inner/super_manager')

@require_http_methods(['GET'])
def change_user_access_level(request):
    if not request.session.get('is_login', None):
        return redirect('/login')

    user_access_level = request.session.get('user_access_level', 0)
    user_name = request.session.get('user_name', 0)
    changed_user_name = request.GET.get('user_name', '')
    access_level = int(request.GET.get('access_level', 0))

    result = inner.change_user_access_level(user_name, user_access_level, changed_user_name, access_level)
    return redirect('/inner/super_manager')