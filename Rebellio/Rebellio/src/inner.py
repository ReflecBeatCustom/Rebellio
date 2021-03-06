import math
from .. import models
from . import utils
from . import constant
from . import fumen_point
from . import config
from .types import inner_types
from .types import pack_types
from django.db.models import Q
import datetime


def delete_absurd_record(delete_absurd_record, session_info):
    """
    删除有问题的记录
    """
    fumen_id = delete_absurd_record.fumen_id
    user_name = delete_absurd_record.user_name
    score = delete_absurd_record.score

    # 得到分数有问题的记录
    records = models.Playrecords.objects.filter(Q(songid=fumen_id) & Q(accountname=user_name) & Q(score=score))
    if len(records) == 0:
        return False
    record = records[0]

    record.delete()
    return True


def view_fumen_comment(view_fumen_comment_params, session_info):
    comment_id = view_fumen_comment_params.comment_id
    if comment_id == 0:
        return False
    comments = models.Playersongcomments.objects.filter(id=comment_id)

    if len(comments) == 0:
        return False
    comment = comments[0]

    fumens = models.Songs.objects.filter(songid=comment.songid)
    if len(fumens) == 0:
        return False
    fumen = fumens[0]

    if fumen.creator != session_info.user_name:
        return False

    models.Playersongcomments.objects.filter(id=comment_id).update(isviewedbyauthor=1, authorviewtime=datetime.datetime.utcnow()+datetime.timedelta(hours=8))
    return True


def get_plan_packs(get_plan_packs_params, pagination_info, session_info):
    sql = "SELECT * FROM plan_pack WHERE category = 3 AND is_published = 0"
    if get_plan_packs_params.keyword != '':
        sql += " AND Title LIKE '%%{0}%%'".format(get_plan_packs_params.keyword)
    sql += " ORDER BY priority DESC, CreateTime DESC"

    unpagination_packs = models.Packs.objects.raw(sql)
    unformated_packs, pagination_info = utils.get_pagination_result(unpagination_packs, pagination_info)
    plan_packs = utils.get_formated_packs(unformated_packs, session_info, [2,3])

    get_plan_packs_response = pack_types.GetPlanPacksResponse(get_plan_packs_params, plan_packs, pagination_info)

    return get_plan_packs_response


def create_plan_pack(create_plan_pack_params):
    """
    创建一个计划包
    """
    pack = models.Packs(category=1, packid=create_plan_pack_params.pack_id, title=create_plan_pack_params.title,
                        comment=create_plan_pack_params.comment, haspromotion=create_plan_pack_params.has_promotion,
                        previewsongid=create_plan_pack_params.preview_song_id)
    pack.save()
    return True


def parse_delete_absurd_record_params(request):
    fumen_id = int(request.GET.get('fumen_id', 0))
    user_name = request.GET.get('user_name', 0)
    score = int(request.GET.get('score', 0))

    delete_absurd_record_params = inner_types.DeleteAbsurdRecordParams(fumen_id, user_name, score)
    return delete_absurd_record_params


def parse_get_plan_packs_params(request):
    keyword = request.GET.get('keyword', '')
    get_plan_packs_params = pack_types.GetPlanPacksParams(keyword)
    return get_plan_packs_params


def parse_view_fumen_comment_params(request):
    comment_id = int(request.GET.get('comment_id', 0))

    view_fumen_comment_params = inner_types.ViewFumenCommentParams(comment_id)
    return view_fumen_comment_params

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
    fumens = models.Songs.objects.filter((Q(diffb__gte=config.need_vote_level) | Q(diffm__gte=config.need_vote_level) | Q(diffh__gte=config.need_vote_level) | Q(diffsp__gte=config.need_vote_level)) & Q(isvotingsubdiff=1))
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

def vote_on_subdiff(vote_on_subdiff_params, session_info):
    if vote_on_subdiff_params.fumen_id == 0 or vote_on_subdiff_params.difficulty == 0:
        return False, "invalid fumen_id or difficulty"

    subdiff_votes = models.Accountsubdiffvoterecord.objects.filter(Q(songid=vote_on_subdiff_params.fumen_id) &
                                                                   Q(difficulty=vote_on_subdiff_params.difficulty) &
                                                                   Q(accountname=session_info.user_name))
    if len(subdiff_votes) == 0:
        subdiff_vote = models.Accountsubdiffvoterecord(accountname=session_info.user_name,
                                                       songid=vote_on_subdiff_params.fumen_id,
                                                       difficulty=vote_on_subdiff_params.difficulty,
                                                       subdiff=vote_on_subdiff_params.subdiff)
        subdiff_vote.save()
        subdiff_vote_point = constant.get_constant(config.subdiff_vote_point_var_name)
        fumen_point.add_fumen_point(session_info.user_name, subdiff_vote_point)
    else:
        subdiff_votes[0].subdiff = vote_on_subdiff_params.subdiff
        subdiff_votes[0].save()
    return True, ""


def parse_vote_on_subdiff_params(request):
    fumen_id = int(request.GET.get('fumen_id', 0))
    subdiff = int(request.GET.get('subdiff', 0))
    difficulty = int(request.GET.get('difficulty', 0))
    return inner_types.VoteOnSubdiffParams(fumen_id, difficulty, subdiff)


def get_subdiff_votes(session_info):
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
        zero_vote_count = 0
        is_voted_by_user = False
        for subdiff_vote in subdiff_votes:
            if subdiff_vote.accountname == session_info.user_name:
                is_voted_by_user = True
            if subdiff_vote.subdiff == 0:
                zero_vote_count += 1
                continue
            vote_count += 1
            total_level += subdiff_vote.subdiff
        if vote_count == 0 or zero_vote_count > vote_count / 2:
            avg_level = '?'
        else:
            avg_level = str(float(total_level / vote_count))

        get_subdiff_votes_response = inner_types.GetSubdiffVotesResponse(fumen_id, title, difficulty, level, avg_level, subdiff_votes, is_voted_by_user)
        result.append(get_subdiff_votes_response)
    return result

def get_advice_fumens(session_info):
    """
    获得当前审核列表的谱面
    """
    unformated_fumens = models.Songs.objects.filter(Q(category=1))

    advice_fumens = []
    for fumen in unformated_fumens:
        if fumen.diffsp != 0:
            difficulty_splitted_fumens = utils.get_difficulty_splitted_fumens([fumen], [3])
            advice_fumens.extend(utils.get_formated_fumens(difficulty_splitted_fumens, session_info))
        else:
            difficulty_splitted_fumens = utils.get_difficulty_splitted_fumens([fumen], [2])
            advice_fumens.extend(utils.get_formated_fumens(difficulty_splitted_fumens, session_info))

    return advice_fumens

def add_subdiff_vote_fumen(user_access_level, fumen_id):
    """
    添加谱面到等级投票中
    """
    if user_access_level < 3 or fumen_id == 0:
        return None

    models.Songs.objects.filter((Q(diffb__gte=config.need_vote_level) | Q(diffm__gte=config.need_vote_level) | Q(diffh__gte=config.need_vote_level) | Q(diffsp__gte=config.need_vote_level)) & Q(songid=fumen_id)).update(isvotingsubdiff=1)
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

    need_vote_subdiff_fumen_diffs = get_need_vote_subdiff_fumen_diffs()
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


def modify_user_fumen_point(session_info, user_name, update_fumen_point):
    if session_info.user_access_level < 3:
        raise Exception("disallowed user")

    fumen_point.add_fumen_point(user_name, update_fumen_point)
    return True


def set_constant(session_info, name, value):
    if session_info.user_access_level < 3:
        raise Exception("disallowed user")

    if name == config.advice_fumen_point_var_name:
        fumen_point.advice_fumen_point = int(value)
    if name == config.subdiff_vote_point_var_name:
        fumen_point.subdiff_vote_point = int(value)
    models.Constants.objects.filter(namevar=name).update(value=value)

    return True
