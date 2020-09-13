import math
from .. import models
from django.db.models import Q

# 默认展示的成绩，评论数量
default_show_count = 10

def set_fumens_format(fumens):
    """
    格式化谱面的格式
    """
    for i in range(len(fumens)):
        # 设置日期格式
        fumens[i].createtime = fumens[i].createtime.strftime('%Y年%m月%d日')

def get_user_high_scores(user_name, view_user_name, access_level):
    sql = "SELECT * FROM (SELECT r.* FROM Playrecords AS r JOIN Songs AS s ON s.SongID = r.SongID LEFT JOIN Unlockrecords AS u on s.SongID = u.SongID WHERE r.AccountName = '{0}' AND (s.AccessLevel <= {1} OR u.AccountName = '{2}')) AS a GROUP BY SongID".format(user_name, access_level, view_user_name)
    played_fumens = models.Songs.objects.raw(sql)
    if len(played_fumens) == 0:
        return []
    played_fumen_dict = {}
    for fumen in played_fumens:
        played_fumen_dict[fumen.songid] = fumen

    high_score_records = []
    for fumen in played_fumens:
        fumen_id = fumen.songid
        records = models.Playrecords.objects.raw("SELECT * FROM Playrecords WHERE SongID = {0} ORDER BY Score DESC LIMIT 1".format(fumen_id))
        if records[0].accountname != user_name:
            continue
        records[0].ranking = 1
        # 设置谱面信息
        fumen = played_fumen_dict[records[0].songid]
        records[0].fumen = fumen
        # 设置日期格式
        records[0].logtime = records[0].logtime.strftime('%Y年%m月%d日 %H时%M分')
        # 设置AR,SR
        records[0].sr = float(str(records[0].sr * 100).split('.')[0] + '.' + str(records[0].sr * 100).split('.')[1][:2])
        records[0].ar = float(str(records[0].ar * 100).split('.')[0] + '.' + str(records[0].ar * 100).split('.')[1][:2])
        # 设置评分(EXC,S,AAA+,AAA,AAA-)
        if records[0].sr >= 100.0 or records[0].ar >= 100.0:
            records[0].rank = 'EXC'
        elif records[0].sr >= 98 or records[0].ar >= 98:
            records[0].rank = 'S'
        elif records[0].sr >= 95 or records[0].ar >= 95:
            records[0].rank = 'AAA+'
        elif records[0].sr >= 90 or records[0].ar >= 90:
            records[0].rank = 'AAA'
        else:
            records[0].rank = 'AAA-'
        high_score_records.append(records[0])
        
    def comparator(x, y):
        if x.ranking < y.ranking:
            return -1
        if x.ranking == y.ranking:
            return 0
        else:
            return 1
    high_score_records = sorted(high_score_records, key=lambda x: x.ranking)

    return high_score_records

def get_user_detail(user_name, view_user_name, access_level):
    """
    获得用户信息
    """
    users = models.Accounts.objects.filter(Q(accountname=user_name))
    if len(users) == 0:
        return None
    user = users[0]

    fumens = models.Songs.objects.raw("SELECT DISTINCT * FROM (SELECT s.* FROM Songs AS s LEFT JOIN Unlockrecords AS u on s.SongID = u.SongID WHERE (s.AccessLevel <= {0} OR u.AccountName = '{1}')) AS result".format(access_level, view_user_name))
    can_view_fumens = {}
    for fumen in fumens:
        can_view_fumens[fumen.songid] = fumen

    recent_records = models.Playrecords.objects.raw("SELECT * FROM Playrecords WHERE AccountName = '{0}' ORDER BY LogTime DESC LIMIT {1}".format(user_name, default_show_count * 5))
    filtered_rencent_records = []
    for i in range(len(recent_records)):
        # 设置谱面信息
        if not can_view_fumens.__contains__(recent_records[i].songid):
            continue
        fumen = can_view_fumens[recent_records[i].songid]
        recent_records[i].fumen = fumen
        # 设置日期格式
        recent_records[i].logtime = recent_records[i].logtime.strftime('%Y年%m月%d日 %H时%M分')
        # 设置AR,SR
        recent_records[i].sr = float(str(recent_records[i].sr * 100).split('.')[0] + '.' + str(recent_records[i].sr * 100).split('.')[1][:2])
        recent_records[i].ar = float(str(recent_records[i].ar * 100).split('.')[0] + '.' + str(recent_records[i].ar * 100).split('.')[1][:2])
        # 设置评分(EXC,S,AAA+,AAA,AAA-)
        if recent_records[i].sr >= 100.0 or recent_records[i].ar >= 100.0:
            recent_records[i].rank = 'EXC'
        elif recent_records[i].sr >= 98 or recent_records[i].ar >= 98:
            recent_records[i].rank = 'S'
        elif recent_records[i].sr >= 95 or recent_records[i].ar >= 95:
            recent_records[i].rank = 'AAA+'
        elif recent_records[i].sr >= 90 or recent_records[i].ar >= 90:
            recent_records[i].rank = 'AAA'
        else:
            recent_records[i].rank = 'AAA-'
        
        filtered_rencent_records.append(recent_records[i])

    user_high_score_records = get_user_high_scores(user_name, view_user_name, access_level)

    result = {'user':user, 'recent_records':filtered_rencent_records[0: default_show_count], 'my_info':'active', 'user_high_score_records': user_high_score_records}
    return result

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