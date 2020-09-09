import math
from .. import models
from django.db.models import Q

def set_return_result(result, sub_page, total, keyword, category, start_page, page_size, total_page, pages):
    """
    设置返回值使其携带传入的参数(使页面更美观，用户使用更方便)
    """
    result[sub_page] = 'active'
    result['sub_page'] = sub_page
    result['keyword'] = keyword
    result['category'] = category
    result['start_page'] = start_page
    result['page_size'] = page_size
    result['total_page'] = total_page
    result['total'] = total
    result['pages'] = pages

def get_packs_format(packs):
    """
    格式化曲包的格式，得到曲包的谱面信息
    """
    result = []
    for i in range(len(packs)):
        pack_id = int(packs[i].packid)
        category = int(packs[i].category)
        fumens = models.Songs.objects.filter(Q(packid=pack_id) & Q(category=category))
        # 设置日期格式
        packs[i].createtime = packs[i].createtime.strftime('%Y年%m月%d日')
        result.append({'pack': packs[i], 'fumens': fumens})
    return result

def get_packs(user_access_level, start_page, page_size, keyword, category):
    sql = "SELECT * FROM Packs WHERE 1=1"
    if keyword != '':
        sql += " AND Title LIKE '%%{0}%%'".format(keyword)
    if user_access_level == 0 and category > 0:
        sql += " AND Category = 0"
    else:
        sql += " AND Category = {0}".format(category)
    sql += " ORDER BY CreateTime DESC"
    packs = models.Packs.objects.raw(sql)
    if len(packs) != 0:
        packs = get_packs_format(packs)

    total = len(packs)
    total_page = math.floor(len(packs) / page_size) + 1
    pages = [i + 1 for i in range(total_page)]
    
    if (start_page - 1) * page_size < len(packs):
        start_index = (start_page - 1) * page_size
    else:
        start_index = 0
        start_page = 1
    end_index = min(start_index + page_size, len(packs))

    return packs[start_index:end_index], total, total_page, pages, start_page

def get_pack(user_access_level, pack_id, category):
    """
    根据曲包id得到曲包信息
    """
    if pack_id == 0:
        return None
    packs = []
    if user_access_level == 0:
        packs = models.Packs.objects.filter(Q(packid=pack_id) & Q(category__lte=0))
    else:
        packs = models.Packs.objects.filter(Q(packid=pack_id) & Q(category=category))
    if len(packs) == 0:
        return None
    packs = get_packs_format(packs)
    return packs[0]
