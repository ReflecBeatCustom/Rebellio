import math
from .. import models
from django.db.models import Q

# 成绩展示框的样式
model_style_high = {'bg':'bg-warning', 'text':'text-black', 'border':'border-warning'}
model_style_medium = {'bg':'bg-success', 'text':'text-white', 'border':'border-success'}
model_style_low = {'bg':'bg-secondary', 'text':'text-white', 'border':'border-secondary'}

# 默认展示的成绩，评论数量
default_show_count = 10

def get_fumen_record(user_name, fumen_id, is_show_all_records):
    records = models.Playrecords.objects.filter(Q(songid=fumen_id) & Q(accountname=user_name)).order_by('-logtime')
    if len(records) == 0:
        return None, records

    best_record = records[0]
    for i in range(len(records)):
        # 设置日期格式
        records[i].logtime = records[i].logtime.strftime('%Y年%m月%d日 %H时%M分')
        # 设置前端样式
        if records[i].score > 3000:
            records[i].bg = model_style_high['bg']
            records[i].text = model_style_high['text']
            records[i].border = model_style_high['border']
        elif records[i].score > 2000:
            records[i].bg = model_style_medium['bg']
            records[i].text = model_style_medium['text']
            records[i].border = model_style_medium['border']
        else:
            records[i].bg = model_style_low['bg']
            records[i].text = model_style_low['text']
            records[i].border = model_style_low['border']
        if records[i].score >= best_record.score:
            best_record = records[i]
        # 设置难度
        if records[i].difficulty == 0:
            records[i].difficulty = "BASIC"
        if records[i].difficulty == 1:
            records[i].difficulty = "MEDIUM"
        if records[i].difficulty == 2:
            records[i].difficulty = "HARD"
        if records[i].difficulty == 3:
            records[i].difficulty = "SPECIAL"
        # 设置AR,SR
        records[i].sr = float(str(records[i].sr * 100).split('.')[0] + '.' + str(records[i].sr * 100).split('.')[1][:2])
        records[i].ar = float(str(records[i].ar * 100).split('.')[0] + '.' + str(records[i].ar * 100).split('.')[1][:2])
        # 设置评分(S,AAA+,AAA,AAA-)
        if records[i].sr >= 98 or records[i].ar > 98:
            records[i].rank = 'S'
        elif records[i].sr >= 95 or records[i].ar > 95:
            records[i].rank = 'AAA+'
        elif records[i].sr >= 90 or records[i].ar > 90:
            records[i].rank = 'AAA'
        else:
            records[i].rank = 'AAA-'

    start_index = 0
    end_index = default_show_count if is_show_all_records == 0 and len(records) >= default_show_count else len(records)
    return best_record, records[start_index:end_index]

def get_fumen_comments(fumen_id, is_show_all_comments):
    comments = models.Playersongcomments.objects.filter(Q(songid=fumen_id)).order_by('-createtime')
    if len(comments) == 0:
        return comments

    for i in range(len(comments)):
        comments[i].createtime = comments[i].createtime.strftime('%Y年%m月%d日 %H:%M:%S')

    start_index = 0
    end_index = default_show_count if is_show_all_comments == 0 and len(comments) >= default_show_count else len(comments)
    return comments[start_index:end_index]

def get_pack_comments(pack_id, is_show_all_comments):
    comments = models.Playerpackcomments.objects.filter(Q(packid=pack_id)).order_by('-createtime')
    if len(comments) == 0:
        return comments

    for i in range(len(comments)):
        comments[i].createtime = comments[i].createtime.strftime('%Y年%m月%d日 %H:%M:%S')

    start_index = 0
    end_index = default_show_count if is_show_all_comments == 0 and len(comments) >= default_show_count else len(comments)
    return comments[start_index:end_index]

def comment_on_fumen(fumen_id, user_name, user_access_level, comment):
    sql = "SELECT s.* FROM Songs AS s LEFT JOIN Unlockrecords AS u on s.SongID = u.SongID WHERE (s.AccessLevel <= {0} OR u.AccountName = '{1}') AND s.SongID = {2}".format(user_access_level, user_name, fumen_id)
    fumens = models.Songs.objects.raw(sql)
    if len(fumens) == 0:
        return False
    if comment == '':
        return False

    comment = models.Playersongcomments(accountname=user_name, songid=fumen_id, comment=comment)
    comment.save()
    return True

def comment_on_pack(pack_id, user_name, user_access_level, comment):
    sql = "SELECT * FROM Packs WHERE PackID = {0}".format(pack_id)
    if user_access_level == 0:
        sql += " AND category = 0"
    packs = models.Packs.objects.raw(sql)
    if len(packs) == 0:
        return False
    if comment == '':
        return False

    comment = models.Playerpackcomments(accountname=user_name, packid=pack_id, comment=comment)
    comment.save()
    return True