# coding = utf-8
import copy
import math
from django.db.models import Q
from .types import http
from .. import models


def get_session_info(request):
    is_login = bool(request.session.get('is_login', False))
    user_access_level = int(request.session.get('user_access_level', 0))
    user_name = request.session.get('user_name', '')
    session_info = http.SessionInfo(is_login, user_name, user_access_level)
    return session_info


def get_pagination_info(request):
    start_page = int(request.GET.get('start_page', 1))
    page_size = int(request.GET.get('page_size', 10))
    pagination_info = http.PaginationInfo(start_page, page_size)
    return pagination_info


def get_pagination_result(result, pagination_info):
    """
    获得分页结果
    """
    if len(result) == 0:
        return []

    total = len(result)
    total_page = math.floor(len(result) / pagination_info.page_size) + 1
    pages = [i + 1 for i in range(total_page)]

    if (pagination_info.start_page - 1) * pagination_info.page_size < len(result):
        start_index = (pagination_info.start_page - 1) * pagination_info.page_size
    else:
        start_index = 0
    end_index = min(start_index + pagination_info.page_size, len(result))

    pagination_info.total = total
    pagination_info.pages = pages
    pagination_info.total_page = total_page

    return result[start_index:end_index], pagination_info


def get_formated_fumens(fumens, difficultys=None):
    """
    标准化谱面的格式

    fumens =
    [
        {
            songid: 123                 # 谱面编号(BASIC,MEDIUM,HARD编号一致,SPECIAL单独编号)
            title: "title"              # 谱面标题
            artist: "artist"            # 歌曲的作者
            creator: "creator"          # 上传者
            chartauthorb: "charauthor"  # BASIC谱作者
            chartauthorm: "charauthor"  # MEDIUM谱作者
            chartauthor: "charauthor"   # HARD或SPECIAL谱作者
            packid: 123                 # 曲包编号,为0则无曲包
            category: 0                 # 类型,0-已发布,1-审核,2-未发布官谱,3-内测
            accesslevel: 0              # 谱面权限,高于权限的用户可查看
            diffb: 0                    # BASIC难度
            diffm: 0                    # MEDIUM难度
            diffh: 0                    # HARD难度
            diffsp: 0                   # SPECIAL难度
            authordescription: ""       # 谱面作者对谱的介绍
            hasspecial: 0               # 该谱是否有special难度谱面,0-有,1-无
            specialid: 0                # 该谱special难度的谱面编号
            createtime: "Sep,7,2020"    # 谱面的上传时间(英文格式)
        },
        ...
    ]

    formated_fumens =
    [
        {
            songid: 123                 # 谱面编号(BASIC,MEDIUM,HARD编号一致,SPECIAL单独编号)
            title: "title"              # 谱面标题
            artist: "artist"            # 歌曲的作者
            creator: "creator"          # 上传者
            chartauthor: "charauthor"   # 该难度的谱面作者
            difficulty: "basic"         # 难度类型,basic,medium,hard,special
            diff: 0                     # 难度数值
            packid: 123                 # 曲包编号,为0则无曲包
            category: 0                 # 类型,0-已发布,1-审核,2-未发布官谱,3-内测
            accesslevel: 0              # 谱面权限,高于权限的用户可查看
            authordescription: ""       # 谱面作者对谱的介绍
            hasspecial: 0               # 该谱是否有special难度谱面,0-有,1-无
            specialid: 0                # 该谱special难度的谱面编号
            createtime: "0000-00-00"    # 谱面的上传时间
        },
        ...
    ]
    """
    formated_fumens = []
    for fumen in fumens:
        # 设置日期格式
        fumen.createtime = fumen.createtime.strftime('%Y-%m-%d')



        # 如果是special难度，直接添加
        if fumen.diffsp != 0 and (difficultys is not None or 3 in difficultys):
            fumen_special = copy.deepcopy(fumen)
            fumen_special.difficulty = 3
            fumen_special.diff = fumen_special.diffsp
            fumen_special.chartauthor = fumen_special.chartauthor
            formated_fumens.append(fumen_special)
            continue

        # 如果不是special难度，拆分为BASIC,MEDIUM,HARD
        fumen_basic = copy.deepcopy(fumen)
        fumen_basic.difficulty = 0
        fumen_basic.diff = fumen_basic.diffb
        fumen_basic.chartauthor = fumen_basic.chartauthorb if fumen_basic.chartauthorb != '' else fumen_basic.chartauthor

        fumen_medium = copy.deepcopy(fumen)
        fumen_medium.difficulty = 1
        fumen_medium.diff = fumen_medium.diffm
        fumen_medium.chartauthor = fumen_medium.chartauthorm if fumen_medium.chartauthorm != '' else fumen_medium.chartauthor

        fumen_hard = copy.deepcopy(fumen)
        fumen_hard.difficulty = 2
        fumen_hard.diff = fumen_hard.diffh
        fumen_hard.chartauthor = fumen_hard.chartauthor

        # 如果传递了difficulty参数，则返回指定难度
        if difficultys is not None:
            if 0 in difficultys:
                formated_fumens.append(fumen_basic)
            if 1 in difficultys:
                formated_fumens.append(fumen_medium)
            if 2 in difficultys:
                formated_fumens.append(fumen_hard)
        else:
            formated_fumens.append(fumen_basic)
            formated_fumens.append(fumen_medium)
            formated_fumens.append(fumen_hard)

    return formated_fumens


def get_formated_packs(packs, difficultys=None):
    """
    格式化曲包的格式，得到曲包的谱面信息
    """
    formated_packs = []
    for pack in packs:
        pack_id = pack.packid
        category = pack.category
        unformated_fumens = models.Songs.objects.filter(Q(packid=pack_id) & Q(category=category))
        fumens = get_formated_fumens(unformated_fumens, difficultys)

        pack.fumens = fumens
        formated_packs.append(pack)

    return formated_packs


def get_formated_records(records, is_ranking=False):
    """
    标准化游玩记录格式
    is_ranking = False # 是否加入排名信息
    """
    formated_records = []
    ranking = 1
    for record in records:
        # 设置日期格式
        record.logtime = record.logtime.strftime('%Y-%m-%d %H:%M')

        # 设置评分(EXC,S,AAA+,AAA,AAA-)
        if record.ar == 0.0:
            record.rank = get_rank_from_rate(record.sr)
        else:
            record.rank = get_rank_from_rate(record.ar)

        # 设置AR,SR
        record.sr = get_percentage_from_rate(record.sr)
        record.ar = get_percentage_from_rate(record.ar)

        # 设置排名信息
        if is_ranking:
            record.ranking = ranking
            ranking += 1

        # 设置用户avatar信息
        accounts = models.Accounts.objects.filter(Q(accountname=record.accountname))
        if len(accounts) == 0:
            record.avatar = 0
        else:
            record.avatar = accounts[0].avatar

        formated_records.append(record)

    return formated_records


def get_formated_comments(comments):
    """
    标准化评论格式
    """
    formated_comments = []
    for comment in comments:
        # 规范化时间
        comment.createtime = comment.createtime.strftime('%Y-%m-%d %H:%M:%S')
        formated_comments.append(comment)
    return formated_comments


def get_rank_from_rate(rate):
    """
    从小数的rate中得到此次记录的ranking
    """
    if rate >= 1.0:
        return 'EXC'
    elif rate >= 0.98:
        return 'S'
    elif rate >= 0.95:
        return 'AAA+'
    elif rate >= 0.90:
        return 'AAA'
    elif rate >= 0.80:
        return 'AA'
    elif rate >= 0.70:
        return 'A'
    elif rate >= 0.60:
        return 'B'
    else:
        return 'C'


def get_percentage_from_rate(rate, precision=2):
    """
    从小数的rate中得到百分比
    precision = 2 # 百分比的精度，默认为小数点后两位
    """
    percentage = float(str(rate * 100).split('.')[0] + '.' + str(rate * 100).split('.')[1][:precision])
    return percentage


