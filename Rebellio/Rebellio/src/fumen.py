import math
from .. import models
from django.db.models import Q

# 默认展示的成绩，评论数量
default_show_count = 10

def set_return_result(result, sub_page, keyword, fumen_creator, category, start_page, page_size, total_page, pages, level):
    """
    设置返回值使其携带传入的参数(使页面更美观，用户使用更方便)
    """
    result[sub_page] = 'active'
    result['sub_page'] = sub_page
    result['keyword'] = keyword
    result['fumen_creator'] = fumen_creator
    result['category'] = category
    result['start_page'] = start_page
    result['page_size'] = page_size
    result['total_page'] = total_page
    result['pages'] = pages
    result['level'] = level

def set_fumens_format(fumens):
    """
    格式化谱面的格式
    """
    for i in range(len(fumens)):
        # 设置日期格式
        fumens[i].createtime = fumens[i].createtime.strftime('%Y年%m月%d日')

def get_fumen_results(fumens, user_name):
    """
    在结果中加入最高成绩和其他信息
    """
    result = []
    for i in range(len(fumens)):
        fumen_id = fumens[i].songid
        player_records = models.Playrecords.objects.filter(Q(songid=fumen_id) & Q(accountname=user_name)).order_by('-score')
        if len(player_records) == 0:
            result.append({'fumen': fumens[i], 'player_best_record': {}})
            continue
        player_best_record = player_records[0]
        sr = round(float((player_best_record.score - player_best_record.jr * 10) * 100 / (player_best_record.note * 3 - 50)), 1)
        rating = 'C'
        if sr >= 98:
            rating = 'S'
        elif sr >= 95:
            rating = 'AAA+'
        elif sr >= 90:
            rating = 'AAA'
        elif sr >= 80:
            rating = 'AA'
        elif sr >= 70:
            rating = 'A'
        elif sr >= 60:
            rating = 'B'
        else:
            rating = 'C'
        result.append({'fumen': fumens[i], 'player_best_record': {'ar': sr, 'score': player_best_record.score, 'jr': player_best_record.jr, 'rating': rating}})
    return result

def get_fumens(keyword, fumen_creator, category, start_page, page_size, level, user_access_level, user_name, is_get_self_create):
    """
    根据关键词(关键词匹配作曲家和曲名)，谱面作者，等级，分页信息和用户权限等级返回谱面列表
    会返回已解锁铺面
    """
    sql = "SELECT DISTINCT * FROM (SELECT s.* FROM Songs AS s LEFT JOIN Unlockrecords AS u on s.SongID = u.SongID WHERE (s.AccessLevel <= {0} OR u.AccountName = '{1}') AND (s.Artist LIKE '%%{2}%%' OR s.Title LIKE '%%{2}%%')".format(user_access_level, user_name, keyword)
    if int(category) != 0:
        sql += ' AND s.Category = {0}'.format(category)
    else:
        sql += ' AND s.Category IN (0,4,5)'
    if is_get_self_create:
        # 返回用户的上传谱面
        sql += " AND s.Creator = '{0}'".format(user_name)
    if fumen_creator != '':
        sql += " AND s.ChartAuthor = '{0}'".format(fumen_creator)
    if level != 0 and level < 13:
        sql += ' AND (s.diffB = {0} OR s.diffM = {0} OR s.diffH = {0} OR s.diffSP = {0})'.format(level)
    elif level >= 13:
        sql += ' AND (s.diffB >= {0} OR s.diffM >= {0} OR s.diffH >= {0} OR s.diffSP >= {0})'.format(level)
    elif level != 0 and level <= 8:
        sql += ' AND (s.diffB <= {0} OR s.diffM <= {0} OR s.diffH <= {0} OR s.diffSP <= {0})'.format(level)
    sql += ') AS result ORDER BY result.CreateTime DESC'
    fumens = models.Songs.objects.raw(sql)
    set_fumens_format(fumens)

    total = len(fumens)
    total_page = math.floor(len(fumens) / page_size) + 1
    pages = [i + 1 for i in range(total_page)]
    
    if (start_page - 1) * page_size < len(fumens):
        start_index = (start_page - 1) * page_size
    else:
        start_index = 0
        start_page = 1
    end_index = min(start_index + page_size, len(fumens))

    return fumens[start_index:end_index], total, total_page, pages, start_page

def get_unlocked_fumens(keyword, fumen_creator, category, start_page, page_size, level, user_access_level, user_name):
    """
    返回解锁铺面
    """
    sql = "SELECT DISTINCT * FROM (SELECT s.* FROM Songs AS s LEFT JOIN Unlockrecords AS u on s.SongID = u.SongID WHERE (s.AccessLevel <= {0} OR u.AccountName = '{1}') AND (s.Artist LIKE '%%{2}%%' OR s.Title LIKE '%%{2}%%') AND s.Category IN (4,5) AND s.AccessLevel > 0".format(user_access_level, user_name, keyword)
    if fumen_creator != '':
        sql += " AND s.ChartAuthor = '{0}'".format(fumen_creator)
    if level != 0 and level < 13:
        sql += ' AND (s.diffB = {0} OR s.diffM = {0} OR s.diffH = {0} OR s.diffSP = {0})'.format(level)
    elif level >= 13:
        sql += ' AND (s.diffB >= {0} OR s.diffM >= {0} OR s.diffH >= {0} OR s.diffSP >= {0})'.format(level)
    elif level != 0 and level <= 8:
        sql += ' AND (s.diffB <= {0} OR s.diffM <= {0} OR s.diffH <= {0} OR s.diffSP <= {0})'.format(level)
    sql += ') AS result ORDER BY result.CreateTime DESC'
    fumens = models.Songs.objects.raw(sql)
    set_fumens_format(fumens)

    total = len(fumens)
    total_page = math.floor(len(fumens) / page_size) + 1
    pages = [i + 1 for i in range(total_page)]
    
    if (start_page - 1) * page_size < len(fumens):
        start_index = (start_page - 1) * page_size
    else:
        start_index = 0
        start_page = 1
    end_index = min(start_index + page_size, len(fumens))

    return fumens[start_index:end_index], total, total_page, pages, start_page

def get_fumen(fumen_id, user_access_level):
    """
    根据谱id名得到谱面信息
    """
    if fumen_id == 0:
        return None
    fumens = models.Songs.objects.filter(Q(songid=fumen_id) & Q(accesslevel__lte=user_access_level))
    if len(fumens) == 0:
        return None
    set_fumens_format(fumens)
    return fumens[0]

def get_fumen_record(user_name, fumen_id, is_show_all_fumen_records, is_special=False):
    """
    根据谱id名得到谱面信息
    """
    unfiltered_records = models.Playrecords.objects.raw("SELECT * FROM Playrecords WHERE SongID = {0} ORDER BY Score DESC".format(fumen_id))
    if len(unfiltered_records) == 0:
        return None, unfiltered_records, None
    
    # 筛选出不同用户的考前成绩
    records = []
    users_set = {}
    for record in unfiltered_records:
        if users_set.__contains__(record.accountname):
            continue
        users_set[record.accountname] = True
        records.append(record)
    
    best_record = records[0]
    for i in range(len(records)):
        # 设置日期格式
        records[i].logtime = records[i].logtime.strftime('%Y年%m月%d日 %H时%M分')
        # 设置难度
        if records[i].difficulty == 3 or (is_special and records[i].difficulty == 0):
            records[i].difficulty = "SPECIAL"
        elif records[i].difficulty == 0:
            records[i].difficulty = "BASIC"
        elif records[i].difficulty == 1:
            records[i].difficulty = "MEDIUM"
        elif records[i].difficulty == 2:
            records[i].difficulty = "HARD"
        # 设置AR,SR
        records[i].sr = float(str(records[i].sr * 100).split('.')[0] + '.' + str(records[i].sr * 100).split('.')[1][:2])
        records[i].ar = float(str(records[i].ar * 100).split('.')[0] + '.' + str(records[i].ar * 100).split('.')[1][:2])
        # 设置评分(EXC,S,AAA+,AAA,AAA-)
        if records[i].sr >= 100.0 or records[i].ar >= 100.0:
            records[i].rank = 'EXC'
        elif records[i].sr >= 98 or records[i].ar >= 98:
            records[i].rank = 'S'
        elif records[i].sr >= 95 or records[i].ar >= 95:
            records[i].rank = 'AAA+'
        elif records[i].sr >= 90 or records[i].ar >= 90:
            records[i].rank = 'AAA'
        else:
            records[i].rank = 'AAA-'
        # 设置排名
        records[i].ranking = i + 1
    
    user_best_record = None
    for i in range(len(records)):
        # 设置用户的最高排名
        if records[i].accountname == user_name:
            user_best_record = records[i]
            break

    start_index = 0
    end_index = default_show_count if is_show_all_fumen_records == 0 and len(records) >= default_show_count else len(records)
    # 如果用户的成绩在返回的成绩列表内，置为None
    if user_best_record and user_best_record.ranking <= default_show_count:
        user_best_record = None

    return best_record, records[start_index + 1:end_index], user_best_record