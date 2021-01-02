from .. import models

def add_fumen_point(user_name, point):
    cur_fumen_points = models.Accounts.objects.filter(accountname=user_name)
    if len(cur_fumen_points) <= 0:
        return
    cur_fumen_point = cur_fumen_points[0].fumen_point
    fumen_point = cur_fumen_point + point
    models.Accounts.objects.filter(accountname=user_name).update(fumen_point=fumen_point)


