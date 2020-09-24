from django.http import HttpResponse
from . import settings
from django.shortcuts import render, redirect
from django.views.decorators.http import require_http_methods
import json
from . import models
from . import forms
from .src import fumen
from .src import utils
from .src import inner
from .src import pack
from .src import user
from .src import decorators


def test(request):
    return HttpResponse(settings.STATICFILES_DIRS)


def home(request):
    return render(request, 'home.html')


"""
登入登出操作
"""


@require_http_methods(['GET', 'POST'])
def login(request):
    if request.session.get('is_login', None):
        return redirect('/home')

    if request.method == "POST":
        login_form = forms.UserForm(request.POST)
        message = "请检查填写的内容！"
        if login_form.is_valid():
            username = login_form.cleaned_data['username']
            password = login_form.cleaned_data['password']
            try:
                results = models.Accounts.objects.raw(
                    "SELECT * FROM Accounts WHERE AccountName = '{0}' AND Passwd = PASSWORD('{1}')".format(username,
                                                                                                           password))
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


@require_http_methods(['GET', 'POST'])
def logout(request):
    if not request.session.get('is_login', None):
        return redirect("/home")
    request.session.flush()
    return redirect("/home")


"""
谱面操作
"""


@require_http_methods(['GET'])
@decorators.is_login_decorator
def get_fumens(request):

    session_info = utils.get_session_info(request)
    pagination_info = utils.get_pagination_info(request)
    get_fumens_params = fumen.parse_get_fumens_params(request, False, False)

    get_fumens_response = fumen.get_fumens(get_fumens_params, pagination_info, session_info)
    return render(request, 'fumen/fumens.html', {'result': get_fumens_response, 'name': 'fumens'})


@require_http_methods(['GET'])
@decorators.is_login_decorator
def get_unlocked_fumens(request):

    session_info = utils.get_session_info(request)
    pagination_info = utils.get_pagination_info(request)
    get_fumens_params = fumen.parse_get_fumens_params(request, True, False)

    get_fumens_response = fumen.get_fumens(get_fumens_params, pagination_info, session_info)
    return render(request, 'fumen/fumens.html', {'result': get_fumens_response, 'name': 'unlocked_fumens'})

@require_http_methods(['GET'])
@decorators.is_login_decorator
def get_own_fumens(request):

    session_info = utils.get_session_info(request)
    pagination_info = utils.get_pagination_info(request)
    get_fumens_params = fumen.parse_get_fumens_params(request, False, True)

    get_fumens_response = fumen.get_fumens(get_fumens_params, pagination_info, session_info)
    return render(request, 'fumen/fumens.html', {'result': get_fumens_response, 'name': 'own_fumens'})


@require_http_methods(['GET'])
@decorators.is_login_decorator
def get_fumen(request):

    session_info = utils.get_session_info(request)
    get_fumen_params = fumen.parse_get_fumen_params(request)

    get_fumen_response = fumen.get_fumen(get_fumen_params, session_info)
    if get_fumen_response is None:
        return redirect('/fumen/fumens')
    return render(request, 'fumen/fumen_detail.html', {'result': get_fumen_response})


@require_http_methods(['GET'])
@decorators.is_login_decorator
def create_fumen_comment(request):

    session_info = utils.get_session_info(request)
    create_fumen_comment_params = fumen.parse_create_fumen_comment_params(request)

    result = fumen.create_fumen_comment(create_fumen_comment_params, session_info)
    return HttpResponse(json.dumps({'result': result}), content_type="application/json")


@require_http_methods(['GET'])
@decorators.is_login_decorator
def update_fumen_comment(request):

    session_info = utils.get_session_info(request)
    update_fumen_comment_params = fumen.parse_update_fumen_comment_params(request)

    result = fumen.update_fumen_comment(update_fumen_comment_params, session_info)
    return HttpResponse(json.dumps({'result': result}), content_type="application/json")


@require_http_methods(['GET'])
@decorators.is_login_decorator
def delete_fumen_comment(request):

    session_info = utils.get_session_info(request)
    delete_fumen_comment_params = fumen.parse_delete_fumen_comment_params(request)

    result = fumen.delete_fumen_comment(delete_fumen_comment_params, session_info)
    return HttpResponse(json.dumps({'result': result}), content_type="application/json")


"""
曲包操作
"""


@require_http_methods(['GET'])
@decorators.is_login_decorator
def get_packs(request):

    session_info = utils.get_session_info(request)
    pagination_info = utils.get_pagination_info(request)
    get_packs_params = pack.parse_get_packs_params(request)

    get_packs_response = pack.get_packs(session_info, pagination_info, get_packs_params)
    return render(request, 'pack/packs.html', {'result': get_packs_response, 'name': 'packs'})


@require_http_methods(['GET'])
@decorators.is_login_decorator
def get_pack(request):

    session_info = utils.get_session_info(request)
    get_pack_params = pack.parse_get_pack_params(request)

    get_pack_response = pack.get_pack(session_info, get_pack_params)
    return render(request, 'pack/pack_detail.html', {'result': get_pack_response, 'name': 'fumens'})


@require_http_methods(['GET'])
@decorators.is_login_decorator
def create_pack_comment(request):
    
    session_info = utils.get_session_info(request)
    create_pack_comment_params = pack.parse_create_pack_comment_params(request)

    result = pack.create_pack_comment(session_info, create_pack_comment_params)
    return HttpResponse(json.dumps({'result': result}), content_type="application/json")


@require_http_methods(['GET'])
@decorators.is_login_decorator
def update_pack_comment(request):

    session_info = utils.get_session_info(request)
    update_pack_comment_params = pack.parse_update_pack_comment_params(request)

    result = pack.update_pack_comment(session_info, update_pack_comment_params)
    return HttpResponse(json.dumps({'result': result}), content_type="application/json")


@require_http_methods(['GET'])
@decorators.is_login_decorator
def delete_pack_comment(request):
    
    session_info = utils.get_session_info(request)
    delete_pack_comment_params = pack.parse_delete_pack_comment_params(request)

    result = pack.delete_pack_comment(session_info, delete_pack_comment_params)
    return HttpResponse(json.dumps({'result': result}), content_type="application/json")


"""
做谱组内部功能
"""

@require_http_methods(['GET'])
def delete_absurd_record(request):

    session_info = utils.get_session_info(request)
    delete_absurd_record_params = inner.parse_delete_absurd_record_params(request)

    result = inner.delete_absurd_record(delete_absurd_record_params, session_info)
    return HttpResponse(json.dumps({'result': result}), content_type="application/json")


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
@decorators.is_login_decorator
@decorators.is_admin_decorator
def get_advice_fumens(request):

    session_info = utils.get_session_info(request)

    fumens = inner.get_advice_fumens(session_info)
    result = {'data': fumens, 'name': 'fumens'}
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
    return render(request, 'inner/super_manager.html',
                  {'need_vote_subdiff_fumen_diffs': need_vote_subdiff_fumen_diffs, 'level1_admins': level1_admins,
                   'level2_admins': level2_admins, 'level3_admins': level3_admins})


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

    user_access_level = request.session.get('user_access_level', 0)

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


@require_http_methods(['GET'])
@decorators.is_login_decorator
@decorators.is_admin_decorator
def view_fumen_comment(request):

    session_info = utils.get_session_info(request)
    view_fumen_comment_params = inner.parse_view_fumen_comment_params(request)

    result = inner.view_fumen_comment(view_fumen_comment_params, session_info)
    return HttpResponse(json.dumps({'result': result}), content_type="application/json")


"""
用户功能
"""


@require_http_methods(['GET'])
@decorators.is_login_decorator
def user_search(request):
    return render(request, 'user/user_search.html', {'name': 'user_search'})


@require_http_methods(['GET'])
@decorators.is_login_decorator
def get_user_detail(request):

    session_info = utils.get_session_info(request)
    get_user_detail_params = user.parse_get_user_detail_params(request)

    result = user.get_user_detail(get_user_detail_params, session_info)
    return render(request, 'user/user_detail.html', {'result': result, 'name': 'user_detail'})


@require_http_methods(['GET'])
@decorators.is_login_decorator
def get_available_avatar(request):

    user_name = request.session.get('user_name', '')

    result = user.get_available_avatar(user_name)
    return render(request, 'user/user_avatar.html', result)


@require_http_methods(['GET'])
@decorators.is_login_decorator
def set_avatar(request):

    user_name = request.session.get('user_name', '')
    avatar_id = request.GET.get('avatar_id', '')

    user.set_avatar(user_name, avatar_id)
    return redirect('/user/user_detail?user_name={0}'.format(user_name))


@require_http_methods(['GET'])
@decorators.is_login_decorator
def user_info_set(request):

    user_name = request.session.get('user_name', '')
    users = models.Accounts.objects.filter(accountname=user_name)
    return render(request, 'user/user_info_set.html', {'user': users[0], 'user_info_set': 'active'})


@require_http_methods(['GET'])
@decorators.is_login_decorator
def set_user_info(request):

    user_name = request.session.get('user_name', '')
    signature = request.GET.get('signature', '')

    user.set_user_info(user_name, signature)

    return redirect('/user/user_info_set?user_name={0}'.format(user_name))
