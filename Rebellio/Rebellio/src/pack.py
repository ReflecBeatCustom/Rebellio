import math
from .. import models
from . import utils
from .types import pack_types
from django.db.models import Q


default_show_count = 10


def get_packs(session_info, pagination_info, get_packs_params):
    sql = "SELECT * FROM Packs WHERE 1=1"
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
        unformated_packs = models.Packs.objects.filter(Q(packid=get_pack_params.pack_id) & Q(category__lte=0))
    else:
        unformated_packs = models.Packs.objects.filter(Q(packid=get_pack_params.pack_id) & Q(category=get_pack_params.category))

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


def get_pack_comments(pack_id, is_show_all_comments):
    comments = models.Playerpackcomments.objects.filter(Q(packid=pack_id)).order_by('-createtime')
    if len(comments) == 0:
        return comments

    for i in range(len(comments)):
        comments[i].createtime = comments[i].createtime.strftime('%Y-%m-%d %H:%M:%S')

    start_index = 0
    end_index = default_show_count if not is_show_all_comments and len(comments) >= default_show_count else len(comments)
    return comments[start_index:end_index]
