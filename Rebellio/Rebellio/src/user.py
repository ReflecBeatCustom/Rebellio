from django.db import connection
import math
from .. import models
from . import utils
from .types import user_types
from django.db.models import Q

# 默认展示的成绩，评论数量
default_show_count = 10


def get_user_detail(get_user_detail_params, session_info):
    users = models.Accounts.objects.filter(Q(accountname=get_user_detail_params.user_name))
    if len(users) == 0:
        return None
    user = users[0]

    # 得到登陆用户可以查看的谱面ID列表
    cur = connection.cursor()
    #cur.execute("SELECT DISTINCT SongID FROM (SELECT s.* FROM Songs AS s LEFT JOIN Unlockrecords AS u on s.SongID = u.SongID WHERE (s.AccessLevel <= {0} OR u.AccountName = '{1}')) AS result".format(session_info.user_access_level, session_info.user_name))
    cur.execute("SELECT DISTINCT SongID FROM (SELECT s.* FROM Songs AS s LEFT JOIN Unlockrecords AS u on s.SongID = u.SongID WHERE (s.AccessLevel <= {0} OR u.AccountName = '{1}')) AS result".format(0, session_info.user_name))
    rows = cur.fetchall()
    can_view_fumen_ids = set([int(row[0]) for row in rows])

    # 得到查看用户的最近游玩记录
    unformated_recent_records = models.Playrecords.objects.raw("SELECT * FROM Playrecords WHERE AccountName = '{0}' ORDER BY LogTime DESC LIMIT {1}".format(get_user_detail_params.user_name, default_show_count))
    player_recent_records = [record for record in utils.get_formated_records(unformated_recent_records) if record.songid in can_view_fumen_ids]
    player_recent_records_with_fumen = get_records_with_fumen(player_recent_records)

    # 得到查看用户的高分记录
    player_high_score_records_with_fumen = get_player_high_records(get_user_detail_params.user_name, can_view_fumen_ids)

    get_user_detail_response = user_types.GetUserDetailResponse(user, player_recent_records_with_fumen, player_high_score_records_with_fumen)
    return get_user_detail_response


def parse_get_user_detail_params(request):
    user_name = request.GET.get('user_name', '')
    get_user_detail_params = user_types.GetUserDetailParams(user_name)
    return get_user_detail_params


def get_records_with_fumen(records):
    """
    record内添加谱面信息
    """
    records_with_fumen = []
    for record in records:
        fumens = models.Songs.objects.filter(Q(songid=record.songid))
        if len(fumens) == 0:
            continue
        fumens = utils.get_formated_fumens(fumens)
        fumen = fumens[0]

        record.fumen = fumen
        records_with_fumen.append(record)
    return records_with_fumen


def get_player_high_records(player_name, can_view_fumen_ids):
    player_high_records = []
    for fumen_id in can_view_fumen_ids:
        # 拿取用户第一的成绩
        records = models.Playrecords.objects.raw("SELECT * FROM Playrecords WHERE SongID = {0} ORDER BY Score DESC LIMIT 1".format(fumen_id))
        records_with_fumen = get_records_with_fumen(utils.get_formated_records(records))
        if len(records_with_fumen) == 0:
            continue
        if records_with_fumen[0].accountname != player_name:
            continue

        record = records_with_fumen[0]
        record.ranking = 1
        player_high_records.append(record)
    return player_high_records


def get_available_avatar(user_name):
    fumens = models.Songs.objects.raw("SELECT DISTINCT * FROM (SELECT s.* FROM Playrecords AS r LEFT JOIN Songs AS s on s.SongID = r.SongID WHERE r.AccountName = '{0}' AND (r.AR >= 0.98 or r.SR >= 0.98)) AS result".format(user_name))
    fumen_ids = [fumen.songid for fumen in fumens]
    return {'avatar_ids': fumen_ids, 'get_available_avatar': 'active'}


def set_avatar(user_name, avatar_id):
    """
    avatar_id就是谱面id
    """
    records = models.Songs.objects.raw("SELECT * FROM Playrecords WHERE AccountName = '{0}' AND SongID = {1} AND (AR >= 0.98 or SR >= 0.98)".format(user_name, avatar_id))
    if len(records) == 0:
        return
    models.Accounts.objects.filter(accountname=user_name).update(avatar=avatar_id)


def set_user_info(user_name, signature):
    models.Accounts.objects.filter(accountname=user_name).update(signature=signature)