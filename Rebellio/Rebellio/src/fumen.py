from django.db import connection
from django.db.models import Q
from . import utils
from .types import fumen_types
from .. import models

# 默认展示的成绩，评论数量
default_show_count = 10


def get_fumens(get_fumens_params, pagination_info, session_info):
    """
    得到谱面列表
    """
    sql = "SELECT DISTINCT * FROM (SELECT s.* FROM Songs AS s LEFT JOIN Unlockrecords AS u on s.SongID = u.SongID WHERE (s.AccessLevel <= {0} OR u.AccountName = '{1}') AND (s.Artist LIKE '%%{2}%%' OR s.Title LIKE '%%{2}%%')".format(
        session_info.user_access_level, session_info.user_name, get_fumens_params.keyword)
    if get_fumens_params.is_get_unlocked:
        # 返回当前用户解锁的谱面
        sql += " AND s.AccessLevel > 0"

    if get_fumens_params.is_get_self_create:
        # 返回当前用户自己上传的谱面
        sql += " AND s.Creator = '{0}'".format(get_fumens_params.fumen_uploader)

    if int(get_fumens_params.category) != 0:
        # category不为0说明是管理员在查询其他类别谱面，直接返回对应类别
        sql += ' AND s.Category = {0}'.format(get_fumens_params.category)
    else:
        # category为0可能是用户在查询谱面，返回4和5(解锁谱面)
        sql += ' AND s.Category IN (0,4,5)'

    if get_fumens_params.fumen_creator != '':
        sql += " AND s.ChartAuthor = '{0}'".format(get_fumens_params.fumen_creator)

    if get_fumens_params.fumen_level != 0 and get_fumens_params.fumen_level < 13:
        sql += ' AND (s.diffB = {0} OR s.diffM = {0} OR s.diffH = {0} OR s.diffSP = {0})'.format(
            get_fumens_params.fumen_level)
    elif get_fumens_params.fumen_level >= 13:
        sql += ' AND (s.diffB >= {0} OR s.diffM >= {0} OR s.diffH >= {0} OR s.diffSP >= {0})'.format(
            get_fumens_params.fumen_level)
    elif get_fumens_params.fumen_level != 0 and get_fumens_params.fumen_level <= 8:
        sql += ' AND (s.diffB <= {0} OR s.diffM <= {0} OR s.diffH <= {0} OR s.diffSP <= {0})'.format(
            get_fumens_params.fumen_level)

    sql += ') AS result ORDER BY result.CreateTime DESC'

    unpagination_fumens = models.Songs.objects.raw(sql)
    unformatted_fumens, pagination_info = utils.get_pagination_result(unpagination_fumens, pagination_info)
    fumens = utils.get_formated_fumens(unformatted_fumens)

    # 得到用户谱面上的最高分
    for i in range(len(fumens)):
        fumen_id = fumens[i].songid
        records = models.Playrecords.objects.raw(
            "SELECT * FROM Playrecords WHERE SongID = {0} AND AccountName = '{1}' AND Difficulty = {2} ORDER BY Score LIMIT 1".format(
                fumen_id, session_info.user_name, fumens[i].difficulty))
        if len(records) == 0:
            continue
        best_record = records[0]
        rate = best_record.ar if best_record.ar != 0.0 else best_record.sr
        best_record.rank = utils.get_rank_from_rate(rate)
        best_record.rate = utils.get_percentage_from_rate(rate)
        fumens[i].best_record = best_record

    get_fumens_response = fumen_types.GetFumensResponse(get_fumens_params, fumens, pagination_info)

    return get_fumens_response


def get_fumen(get_fumen_params, session_info):
    """
    根据谱面ID得到谱面信息
    """
    if get_fumen_params.fumen_id == 0:
        return None

    unformatted_fumens = models.Songs.objects.filter(
        Q(songid=get_fumen_params.fumen_id) & Q(accesslevel__lte=session_info.user_access_level))
    if len(unformatted_fumens) == 0:
        return None

    fumens = utils.get_formated_fumens(unformatted_fumens, [get_fumen_params.difficulty])
    if len(fumens) == 0:
        return None

    # 得到用户的游玩记录
    fumen_player_records = get_fumen_player_records(get_fumen_params.fumen_id, get_fumen_params.difficulty,
                                                    session_info.user_name,
                                                    get_fumen_params.is_show_all_fumen_player_records)
    fumen_player_best_record = get_fumen_best_record(get_fumen_params.fumen_id, get_fumen_params.difficulty,
                                                     session_info.user_name)

    # 得到谱面的所有玩家游玩记录
    fumen_records = get_fumen_records(get_fumen_params.fumen_id, get_fumen_params.difficulty,
                                      get_fumen_params.is_show_all_fumen_records)
    if len(fumen_records) == 0:
        fumen_best_record = None
    else:
        fumen_best_record = fumen_records[0]
    fumen_records = fumen_records[1:]

    # 得到谱面的评论记录
    fumen_comments = get_fumen_comments(get_fumen_params.fumen_id, get_fumen_params.is_show_all_comments)

    get_fumen_response = fumen_types.GetFumenResponse(get_fumen_params, fumens[0], fumen_records, fumen_best_record,
                                                      fumen_player_records, fumen_player_best_record, fumen_comments)
    return get_fumen_response


def parse_get_fumens_params(request, is_get_unlocked=False, is_get_self_create=False):
    keyword = request.GET.get('keyword', '')
    fumen_creator = request.GET.get('fumen_creator', '')
    category = int(request.GET.get('category', 0))
    fumen_level = int(request.GET.get('fumen_level', 0))
    get_fumens_params = fumen_types.GetFumensParams(keyword, fumen_creator, category, fumen_level, is_get_unlocked,
                                                    is_get_self_create)
    if is_get_self_create:
        get_fumens_params.fumen_uploader = request.session.get('user_name', '')
    return get_fumens_params


def parse_get_fumen_params(request):
    fumen_id = int(request.GET.get('fumen_id', 0))
    difficulty = int(request.GET.get('difficulty', 2))
    is_show_all_fumen_records = int(request.GET.get('is_show_all_fumen_records', 0))
    is_show_all_fumen_player_records = int(request.GET.get('is_show_all_fumen_player_records', 0))
    is_show_all_comments = int(request.GET.get('is_show_all_comments', 0))
    get_fumen_params = fumen_types.GetFumenParams(fumen_id, difficulty, is_show_all_fumen_records == 1,
                                                  is_show_all_fumen_player_records == 1,
                                                  is_show_all_comments == 1)
    return get_fumen_params


def get_fumen_player_records(fumen_id, difficulty, user_name, is_show_all_fumen_player_records):
    """
    得到玩家的谱面游玩记录
    """
    unpagination_records = models.Playrecords.objects.filter(
        Q(songid=fumen_id) & Q(difficulty=difficulty) & Q(accountname=user_name)).order_by('-logtime')
    if len(unpagination_records) == 0:
        return []

    start_index = 0
    end_index = default_show_count if not is_show_all_fumen_player_records and len(
        unpagination_records) >= default_show_count else len(unpagination_records)
    unformated_records = unpagination_records[start_index:end_index]

    records = utils.get_formated_records(unformated_records)
    return records


def get_fumen_best_record(fumen_id, difficulty, user_name=''):
    """
    得到玩家的谱面最佳游玩记录，如果user_name为空则得到谱面的最佳记录
    """
    if user_name == '':
        unformated_records = models.Playrecords.objects.filter(Q(songid=fumen_id) & Q(difficulty=difficulty)).order_by(
            '-score')
    else:
        unformated_records = models.Playrecords.objects.filter(
            Q(songid=fumen_id) & Q(difficulty=difficulty) & Q(accountname=user_name)).order_by('-score')
    if len(unformated_records) == 0:
        return None

    records = utils.get_formated_records(unformated_records)
    if len(records) == 0:
        return None
    record = records[0]

    # 得到这个最高成绩的排名
    cur = connection.cursor()
    cur.execute(
        "SELECT COUNT(*) AS count FROM (SELECT DISTINCT AccountName FROM Playrecords WHERE Score > {0} AND SongID = {1} AND Difficulty = {2}) AS a".format(
            record.score, record.songid, record.difficulty))
    record.ranking = cur.fetchone()[0] + 1

    return record


def get_fumen_records(fumen_id, difficulty, is_show_all_fumen_records):
    """
    得到所有玩家的游玩记录
    """
    unpagination_records = models.Playrecords.objects.raw(
        "SELECT * FROM (SELECT AccountName, MAX(Score) AS Score, SongID, Difficulty, LogTime, JR, Note, SR, id, AR FROM Playrecords WHERE SongID = {0} AND Difficulty = {1} GROUP BY AccountName) AS a ORDER BY Score DESC, LogTime".format(
            fumen_id, difficulty))
    if len(unpagination_records) == 0:
        return []

    start_index = 0
    end_index = default_show_count if not is_show_all_fumen_records and len(
        unpagination_records) >= default_show_count else len(unpagination_records)
    unformated_records = unpagination_records[start_index:end_index]

    records = utils.get_formated_records(unformated_records, True)
    return records


def get_fumen_comments(fumen_id, is_show_all_comments):
    """
    得到谱面的用户评论记录
    """
    unpagination_comments = models.Playersongcomments.objects.filter(Q(songid=fumen_id)).order_by('-createtime')
    if len(unpagination_comments) == 0:
        return []

    start_index = 0
    end_index = default_show_count if is_show_all_comments and len(
        unpagination_comments) >= default_show_count else len(unpagination_comments)
    unformated_comments = unpagination_comments[start_index:end_index]

    comments = utils.get_formated_comments(unformated_comments)

    return comments


def create_fumen_comment(create_fumen_comment_params, session_info):
    if create_fumen_comment_params.comment == '':
        return False

    # 验证用户是否可以查看这个谱面
    cur = connection.cursor()
    cur.execute(
        "SELECT COUNT(*) FROM Songs AS s LEFT JOIN Unlockrecords AS u on s.SongID = u.SongID WHERE (s.AccessLevel <= {0} OR u.AccountName = '{1}') AND s.SongID = {2}".format(
            session_info.user_access_level, session_info.user_name, create_fumen_comment_params.fumen_id))
    rows = cur.fetchall()
    if len(rows) == 0:
        return False

    comment = models.Playersongcomments(accountname=session_info.user_name, songid=create_fumen_comment_params.fumen_id, comment=create_fumen_comment_params.comment)
    comment.save()
    return True


def update_fumen_comment(update_fumen_comment_params, session_info):
    if update_fumen_comment_params.comment == '':
        return False

    # 验证用户是否可以修改这个评论
    cur = connection.cursor()
    cur.execute("SELECT AccountName FROM PlayerSongComments WHERE id = {0}".format(update_fumen_comment_params.comment_id))
    rows = cur.fetchall()
    if len(rows) == 0:
        return False
    if rows[0][0] != session_info.user_name and session_info.user_access_level < 1:
        return False

    comment = models.Playersongcomments.objects.filter(id=update_fumen_comment_params.comment_id).update(comment=update_fumen_comment_params.comment)
    return True


def delete_fumen_comment(delete_fumen_comment_params, session_info):
    if delete_fumen_comment_params.comment_id == 0:
        return False

    # 验证用户是否可以删除这个评论
    cur = connection.cursor()
    cur.execute("SELECT AccountName FROM PlayerSongComments WHERE id = {0}".format(delete_fumen_comment_params.comment_id))
    rows = cur.fetchall()
    if len(rows) == 0:
        return False
    if rows[0][0] != session_info.user_name and session_info.user_access_level < 1:
        return False

    models.Playersongcomments.objects.filter(id=delete_fumen_comment_params.comment_id).delete()
    return True


def parse_create_fumen_comment_params(request):
    fumen_id = int(request.GET.get('fumen_id', 0))
    difficulty = int(request.GET.get('difficulty', 0))
    comment = request.GET.get('comment', '')
    create_fumen_comment_params = fumen_types.CreateFumenCommentParams(fumen_id, difficulty, comment)
    return create_fumen_comment_params


def parse_update_fumen_comment_params(request):
    comment_id = int(request.GET.get('comment_id', 0))
    difficulty = int(request.GET.get('difficulty', 0))
    comment = request.GET.get('comment', '')
    update_fumen_comment_params = fumen_types.UpdateFumenCommentParams(comment_id, difficulty, comment)
    return update_fumen_comment_params


def parse_delete_fumen_comment_params(request):
    comment_id = int(request.GET.get('comment_id', 0))
    fumen_id = int(request.GET.get('fumen_id', 0))
    difficulty = int(request.GET.get('difficulty', 0))
    delete_fumen_comment_params = fumen_types.DeleteFumenCommentParams(comment_id, fumen_id, difficulty)
    return delete_fumen_comment_params
