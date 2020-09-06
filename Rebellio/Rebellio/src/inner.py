import math
from .. import models
from . import fumen
from django.db.models import Q

need_vote_level = 10

def set_return_result(result, sub_page):
    """
    设置返回值使其携带传入的参数(使页面更美观，用户使用更方便)
    """
    result[sub_page] = 'active'
    result['sub_page'] = sub_page

def get_need_vote_subdiff_fumen_diffs(user_access_level):
    """
    返回当前需要投票subdiff的谱面id和难度id列表
    """
    if user_access_level < 1:
        return []

    fumens = models.Songs.objects.filter((Q(diffb__gte=need_vote_level) | Q(diffm__gte=need_vote_level) | Q(diffh__gte=need_vote_level) | Q(diffsp__gte=need_vote_level)) & Q(isvotingsubdiff=1))
    result = []
    for fumen in fumens:
        fumen_id = fumen.songid
        title = fumen.title
        if fumen.diffb >= 10:
            result.append({'title': title, 'fumen_id': fumen_id, 'difficulty': 0, 'level': fumen.diffb})
        if fumen.diffm >= 10:
            result.append({'title': title, 'fumen_id': fumen_id, 'difficulty': 1, 'level': fumen.diffm})
        if fumen.diffh >= 10:
            result.append({'title': title, 'fumen_id': fumen_id, 'difficulty': 2, 'level': fumen.diffh})
        if fumen.diffsp >= 10:
            result.append({'title': title, 'fumen_id': fumen_id, 'difficulty': 3, 'level': fumen.diffsp})
    return result

def vote_on_subdiff(fumen_id, difficulty, user_name, user_access_level, subdiff):
    if fumen_id == 0 or difficulty == 0 or user_access_level < 1 or subdiff < 0:
        return None
    subdiff_votes = models.Accountsubdiffvoterecord.objects.filter(Q(songid=fumen_id) & Q(difficulty=difficulty) & Q(accountname=user_name))
    if len(subdiff_votes) == 0:
        subdiff_vote = models.Accountsubdiffvoterecord(accountname=user_name, songid=fumen_id, difficulty=difficulty, subdiff=subdiff)
        subdiff_vote.save()
    else:
        subdiff_votes[0].subdiff = subdiff
        subdiff_votes[0].save()
    return True

def get_subdiff_vote(user_name, user_access_level):
    if user_access_level < 1:
        return None
    need_vote_subdiff_fumen_diffs = get_need_vote_subdiff_fumen_diffs(user_access_level)
    result = []
    for fumen_diff in need_vote_subdiff_fumen_diffs:
        title = fumen_diff['title']
        fumen_id = fumen_diff['fumen_id']
        difficulty = fumen_diff['difficulty']
        level = fumen_diff['level']
        subdiff_votes = models.Accountsubdiffvoterecord.objects.filter(Q(songid=fumen_id) & Q(difficulty=difficulty))

        total_level = 0
        vote_count = 0
        zero_vote_count = 0
        avg_level = 0
        for subdiff_vote in subdiff_votes:
            if subdiff_vote.subdiff == 0:
                zero_vote_count += 1
                continue
            vote_count += 1
            total_level += subdiff_vote.subdiff
        if vote_count == 0 or zero_vote_count > vote_count / 2:
            avg_level = '?'
        else:
            avg_level = str(float(total_level / vote_count))

        result.append({'title': title, 'difficulty': difficulty, 'level': level, 'fumen_id': fumen_id, 'avg_level': avg_level, 'subdiff_votes': subdiff_votes})
    return result

def get_advice_fumens(user_access_level):
    """
    获得当前审核列表的谱面
    """
    if user_access_level < 1:
        return None

    fumens = models.Songs.objects.filter(Q(category=1))
    fumen.set_fumens_format(fumens)
    return fumens

def add_subdiff_vote_fumen(user_access_level, fumen_id):
    """
    添加谱面到等级投票中
    """
    if user_access_level < 3 or fumen_id == 0:
        return None

    models.Songs.objects.filter((Q(diffb__gte=need_vote_level) | Q(diffm__gte=need_vote_level) | Q(diffh__gte=need_vote_level) | Q(diffsp__gte=need_vote_level)) & Q(songid=fumen_id)).update(isvotingsubdiff=1)
    return True

def delete_subdiff_vote_fumen(user_access_level, fumen_id):
    """
    等级投票中删除投票谱面
    """
    if user_access_level < 3 or fumen_id == 0:
        return None

    models.Songs.objects.filter(Q(songid=fumen_id)).update(isvotingsubdiff=0)
    return True

def update_packs(user_access_level):
    """
    发布一个包，将发布池中的包放入待审核中
    """
    # TODO
    return True

def update_subdiffs(user_access_level):
    """
    更新当前的谱面等级投票
    """
    if user_access_level < 3:
        return None

    need_vote_subdiff_fumen_diffs = get_need_vote_subdiff_fumen_diffs(user_access_level)
    for fumen_diff in need_vote_subdiff_fumen_diffs:
        fumen_id = fumen_diff['fumen_id']
        difficulty = fumen_diff['difficulty']
        subdiff_votes = models.Accountsubdiffvoterecord.objects.filter(Q(songid=fumen_id) & Q(difficulty=difficulty))

        total_level = 0
        vote_count = 0
        vote_count_zero = 0
        avg_level = 0
        for subdiff_vote in subdiff_votes:
            if subdiff_vote.subdiff == 0:
                vote_count_zero += 1
            vote_count += 1
            total_level += subdiff_vote.subdiff
        if vote_count == 0 or vote_count_zero > vote_count / 2:
            # 如果没有人投票或？数量投票多于一半，则设置为？
            avg_level = 0
        else:
            avg_level = int(total_level / vote_count)

        if difficulty == 0:
            models.Songs.objects.filter(Q(songid=fumen_id)).update(isvotingsubdiff=0,subdiffb=avg_level)
        elif difficulty == 1:
            models.Songs.objects.filter(Q(songid=fumen_id)).update(isvotingsubdiff=0,subdiffm=avg_level)
        elif difficulty == 2:
            models.Songs.objects.filter(Q(songid=fumen_id)).update(isvotingsubdiff=0,subdiffh=avg_level)
        elif difficulty == 3:
            models.Songs.objects.filter(Q(songid=fumen_id)).update(isvotingsubdiff=0,subdiffsp=avg_level)
    return True

def get_admins(user_access_level):
    level1_admins = []
    level2_admins = []
    level3_admins = []

    if user_access_level < 3:
        return level1_admins, level2_admins, level3_admins
    
    admins = models.Accounts.objects.filter(Q(accesslevel__gte=1))
    for admin in admins:
        if admin.accesslevel == 1:
            level1_admins.append(admin.accountname)
        if admin.accesslevel == 2:
            level2_admins.append(admin.accountname)
        if admin.accesslevel == 3:
            level3_admins.append(admin.accountname)
    return level1_admins, level2_admins, level3_admins

def change_user_access_level(user_name, user_access_level, changed_user_name, access_level):
    if user_access_level < 3 or user_name == changed_user_name:
        return False
    
    models.Accounts.objects.filter(Q(accountname=changed_user_name)).update(accesslevel=access_level)
    return True
