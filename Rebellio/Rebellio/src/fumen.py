import math
from .. import models
from django.db.models import Q

# 默认展示的成绩，评论数量
default_show_count = 4

def set_return_result(result, sub_page, keyword, fumen_creator, category, start_page, page_size, total_page, pages, level):
    """
    设置返回值使其携带传入的参数(使页面更美观，用户使用更方便)
    """
    result[sub_page] = 'active'
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
        # 设置谱面优先级
        if fumens[i].accesslevel == 0:
            fumens[i].accesslevel = '公共'
        if fumens[i].accesslevel == 1:
            fumens[i].accesslevel = '内测'
        if fumens[i].accesslevel == 2:
            fumens[i].accesslevel = '未发布官谱'
        if fumens[i].accesslevel == 3:
            fumens[i].accesslevel = '私人'
        # 设置曲包ID
        if fumens[i].packid == 0:
            fumens[i].packid = '未发布'
        # 设置难度
        if fumens[i].diffsp == 0:
            fumens[i].diffsp = '-'

def get_fumens(keyword, fumen_creator, category, start_page, page_size, level, user_access_level, user_name):
    """
    根据关键词(关键词匹配作曲家和曲名)，谱面作者，等级，分页信息和用户权限等级返回谱面列表
    """
    cmd = 'models.Songs.objects.filter((Q(title__icontains=keyword) | Q(artist__icontains=keyword)) & Q(category=category)'
    if user_name != '':
        # 如果用户名不为空，则返回用户的上传谱面
        cmd += ' & Q(creator=user_name)'
    else:
        # 如果用户名为空，则返回用户权限可以查看的谱面
        cmd += ' & Q(accesslevel__lte=user_access_level)'
    if fumen_creator != '':
        cmd += ' & Q(chartauthor__icontains=fumen_creator)'
    if level != 0 and level < 13:
        cmd += ' & (Q(diffb=level) | Q(diffm=level) | Q(diffh=level) | Q(diffsp=level))'
    if level >= 13:
        cmd += ' & (Q(diffb__gt=12) | Q(diffm__gt=12) | Q(diffh__gt=12) | Q(diffsp__gt=12))'
    cmd += ').order_by("-createtime")'
    fumens = eval(cmd)
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

def get_fumen_record(fumen_id, is_show_all_fumen_records):
    """
    根据谱id名得到谱面信息
    """
    records = models.Playrecords.objects.filter(Q(songid=fumen_id)).order_by('-score')
    if len(records) == 0:
        return None, records
    
    best_record = records[0]
    for i in range(len(records)):
        # 设置日期格式
        records[i].logtime = records[i].logtime.strftime('%Y年%m月%d日 %h时%M分')
        if records[i].score >= best_record.score:
            best_record = records[i]
        # 设置难度
        if records[i].difficulty == 0:
            records[i].difficulty = "BASIC"
        if records[i].difficulty == 1:
            records[i].difficulty = "NORMAL"
        if records[i].difficulty == 2:
            records[i].difficulty = "HARD"
        if records[i].difficulty == 3:
            records[i].difficulty = "SPECIAL"

    start_index = 0
    end_index = default_show_count if is_show_all_fumen_records == 0 and len(records) >= default_show_count else len(records)
    return best_record, records[start_index:end_index]