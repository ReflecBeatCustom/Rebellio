import math
from django.db import connection
from .. import models
from . import utils
from .types import pack_types
from django.db.models import Q


default_show_count = 20


def get_packs(session_info, pagination_info, get_packs_params):
    sql = "SELECT * FROM Packs WHERE IFNULL(is_visible, 0, 1) = 1"
    if get_packs_params.keyword != '':
        sql += " AND Title LIKE '%%{0}%%'".format(get_packs_params.keyword)
    if session_info.user_access_level < 1 and get_packs_params.category > 0:
        sql += " AND Category = 0"
    else:
        sql += " AND Category = {0}".format(get_packs_params.category)
    sql += " ORDER BY CreateTime DESC"

    unpagination_packs = models.Packs.objects.raw(sql)
    unformated_packs, pagination_info = utils.get_pagination_result(unpagination_packs, pagination_info)
    packs = utils.get_formated_packs(unformated_packs, session_info, [2,3])

    get_packs_response = pack_types.GetPacksResponse(get_packs_params, packs, pagination_info)

    return get_packs_response


def get_pack(session_info, get_pack_params):
    """
    根据曲包id得到曲包信息
    """
    if get_pack_params.pack_id == 0:
        return None

    if session_info.user_access_level == 0:
        unformated_packs = models.Packs.objects.filter(Q(packid=get_pack_params.pack_id) & Q(category__lte=0) & Q(is_visible=1))
    else:
        unformated_packs = models.Packs.objects.filter(Q(packid=get_pack_params.pack_id) & Q(category=get_pack_params.category) & Q(is_visible=1))

    # 得到曲包结果
    packs = utils.get_formated_packs(unformated_packs, session_info)
    if len(packs) == 0:
        return None
    pack = packs[0]

    # 得到用户谱面上的最高分
    for i in range(len(pack.fumens)):
        fumen_id = pack.fumens[i].songid
        records = models.Playrecords.objects.raw(
            "SELECT * FROM Playrecords WHERE SongID = {0} AND AccountName = '{1}' AND Difficulty = {2} ORDER BY Score LIMIT 1".format(
                fumen_id, session_info.user_name, pack.fumens[i].difficulty))
        if len(records) == 0:
            continue
        best_record = records[0]
        rate = best_record.ar if best_record.ar != 0.0 else best_record.sr
        best_record.rank = utils.get_rank_from_rate(rate)
        best_record.rate = utils.get_percentage_from_rate(rate)
        pack.fumens[i].best_record = best_record

    # 获得曲包的评论
    pack_comments = get_pack_comments(pack.packid, get_pack_params.is_show_all_pack_comments)

    get_pack_response = pack_types.GetPackResponse(get_pack_params, pack, pack_comments)

    return get_pack_response


def create_pack_comment(session_info, create_pack_comment_params):
    if create_pack_comment_params.comment == '':
        return False

    sql = "SELECT * FROM Packs WHERE PackID = {0}".format(create_pack_comment_params.pack_id)
    if session_info.user_access_level == 0:
        sql += " AND category = 0"
    packs = models.Packs.objects.raw(sql)
    if len(packs) == 0:
        return False

    comment = models.Playerpackcomments(accountname=session_info.user_name, packid=create_pack_comment_params.pack_id, comment=create_pack_comment_params.comment)
    comment.save()
    return True


def get_pack_comments(pack_id, is_show_all_comments):
    comments = models.Playerpackcomments.objects.filter(Q(packid=pack_id)).order_by('-createtime')
    if len(comments) == 0:
        return comments

    for i in range(len(comments)):
        comments[i].createtime = comments[i].createtime.strftime('%Y-%m-%d %H:%M:%S')

    start_index = 0
    end_index = default_show_count if not is_show_all_comments and len(comments) >= default_show_count else len(comments)
    return comments[start_index:end_index]


def update_pack_comment(session_info, update_pack_comment_params):
    if update_pack_comment_params.comment == '' or update_pack_comment_params.comment_id == 0:
        return False

    # 验证用户是否可以修改这个评论
    cur = connection.cursor()
    cur.execute("SELECT AccountName FROM PlayerPackComments WHERE id = {0}".format(update_pack_comment_params.comment_id))
    rows = cur.fetchall()
    if len(rows) == 0:
        return False
    if rows[0][0] != session_info.user_name and session_info.user_access_level < 1:
        return False

    models.Playerpackcomments.objects.filter(id=update_pack_comment_params.comment_id).update(comment=update_pack_comment_params.comment)
    return True


def delete_pack_comment(session_info, delete_pack_comment_params):
    if delete_pack_comment_params.comment_id == 0:
        return False

    # 验证用户是否可以删除这个评论
    cur = connection.cursor()
    cur.execute("SELECT AccountName FROM PlayerPackComments WHERE id = {0}".format(delete_pack_comment_params.comment_id))
    rows = cur.fetchall()
    if len(rows) == 0:
        return False
    if rows[0][0] != session_info.user_name and session_info.user_access_level < 1:
        return False

    models.Playerpackcomments.objects.filter(id=delete_pack_comment_params.comment_id).delete()
    return True


def parse_get_packs_params(request):
    keyword = request.GET.get('keyword', '')
    category = request.GET.get('category', 0)
    get_packs_params = pack_types.GetPacksParams(keyword, category)
    return get_packs_params


def parse_get_pack_params(request):
    pack_id = int(request.GET.get('pack_id', 0))
    category = int(request.GET.get('category', 0))
    is_show_all_pack_comments = bool(request.GET.get('is_show_all_pack_comments', False))
    get_pack_params = pack_types.GetPackParams(pack_id, category, is_show_all_pack_comments)
    return get_pack_params


def parse_create_pack_comment_params(request):
    pack_id = int(request.GET.get('pack_id', 0))
    comment = request.GET.get('comment', 0)
    create_pack_comment_params = pack_types.CreatePackCommentParams(pack_id, comment)
    return create_pack_comment_params


def parse_update_pack_comment_params(request):
    pack_id = int(request.GET.get('pack_id', 0))
    comment_id = int(request.GET.get('comment_id', 0))
    comment = request.GET.get('comment', 0)
    update_pack_comment_params = pack_types.UpdatePackCommentParams(pack_id, comment_id, comment)
    return update_pack_comment_params


def parse_delete_pack_comment_params(request):
    pack_id = int(request.GET.get('pack_id', 0))
    comment_id = int(request.GET.get('comment_id', 0))
    delete_pack_comment_params = pack_types.DeletePackCommentParams(pack_id, comment_id)
    return delete_pack_comment_params
