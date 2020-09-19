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

    start_index = 0
    end_index = default_show_count if is_show_all_records == 0 and len(records) >= default_show_count else len(records)
    return best_record, records[start_index:end_index]
    