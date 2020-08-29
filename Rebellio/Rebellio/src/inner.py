import math
from .. import models
from django.db.models import Q

def set_return_result(result, sub_page):
    """
    设置返回值使其携带传入的参数(使页面更美观，用户使用更方便)
    """
    result[sub_page] = 'active'
    result['sub_page'] = sub_page

def get_need_vote_subdiff_fumen_diffs():
    """
    返回当前需要投票subdiff的谱面id和难度id列表
    """
    fumens = models.Songs.objects.filter((Q(diffb__lte=10) | Q(diffm__lte=10) | Q(diffh__lte=10) | Q(diffsp__lte=10)) & Q(isvotingsubdiff=1))
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
    need_vote_subdiff_fumen_diffs = get_need_vote_subdiff_fumen_diffs()
    result = []
    for fumen_diff in need_vote_subdiff_fumen_diffs:
        title = fumen_diff['title']
        fumen_id = fumen_diff['fumen_id']
        difficulty = fumen_diff['difficulty']
        level = fumen_diff['level']
        subdiff_votes = models.Accountsubdiffvoterecord.objects.filter(Q(songid=fumen_id) & Q(difficulty=difficulty))

        total_level = 0
        vote_count = 0
        avg_level = 0
        for subdiff_vote in subdiff_votes:
            vote_count += 1
            total_level += subdiff_vote.subdiff
        if vote_count == 0:
            avg_level = '0'
        else:
            avg_level = str(float(total_level / vote_count))

        result.append({'title': title, 'difficulty': difficulty, 'level': level, 'fumen_id': fumen_id, 'avg_level': avg_level, 'subdiff_votes': subdiff_votes})
    return result
