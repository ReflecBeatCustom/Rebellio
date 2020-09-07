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

    recent_records = models.Playrecords.objects.raw("SELECT * FROM Playrecords WHERE AccountName = '{0}' ORDER BY Score DESC LIMIT {1}".format(user_name, default_show_count * 5))
    filtered_rencent_records = []
    for i in range(len(recent_records)):
        # 设置谱面信息
        if not can_view_fumens.__contains__(recent_records[i].songid):
            continue
        fumen = can_view_fumens[recent_records[i].songid]
        recent_records[i].fumen = fumen
        # 设置日期格式
        recent_records[i].logtime = recent_records[i].logtime.strftime('%Y年%m月%d日 %H时%M分')
        # 设置难度
        if recent_records[i].difficulty == 3 or (fumen.diffsp != 0 and recent_records[i].difficulty == 0):
            recent_records[i].difficulty = "SPECIAL"
        elif recent_records[i].difficulty == 0:
            recent_records[i].difficulty = "BASIC"
        elif recent_records[i].difficulty == 1:
            recent_records[i].difficulty = "MEDIUM"
        elif recent_records[i].difficulty == 2:
            recent_records[i].difficulty = "HARD"
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

    result = {'user':user, 'recent_records':filtered_rencent_records[0: default_show_count]}
    return result
