class GetFumensParams(object):
    def __init__(self, keyword, fumen_creator, category, fumen_level, is_get_unlocked, is_get_self_create):
        self.keyword = keyword
        self.fumen_creator = fumen_creator
        self.category = category
        self.fumen_level = fumen_level
        self.is_get_unlocked = is_get_unlocked
        self.is_get_self_create = is_get_self_create

class GetFumensResponse(object):
    def __init__(self, get_fumens_params, fumens, pagination_info):
        self.get_fumens_params = get_fumens_params
        self.fumens = fumens
        self.pagination_info = pagination_info


class GetFumenParams(object):
    def __init__(self, fumen_id, difficulty, is_show_all_fumen_records, is_show_all_fumen_player_records, is_show_all_comments):
        self.fumen_id = fumen_id
        self.difficulty = difficulty
        self.is_show_all_fumen_records = is_show_all_fumen_records
        self.is_show_all_fumen_player_records = is_show_all_fumen_player_records
        self.is_show_all_comments = is_show_all_comments


class GetFumenResponse(object):
    def __init__(self, get_fumen_params, fumen, fumen_records, fumen_best_record, fumen_player_records, fumen_player_best_record, fumen_comments):
        """
        fumen_records内不包含最高分
        fumen_player_records内包含最高分
        """
        self.get_fumen_params = get_fumen_params
        self.fumen = fumen
        self.fumen_records = fumen_records
        self.fumen_best_record = fumen_best_record
        self.fumen_player_records = fumen_player_records
        self.fumen_player_best_record = fumen_player_best_record
        self.fumen_comments = fumen_comments

class CreateFumenCommentParams(object):
    def __init__(self, fumen_id, difficulty, comment, is_ok):
        self.fumen_id = fumen_id
        self.difficulty = difficulty
        self.comment = comment
        self.is_ok = is_ok


class UpdateFumenCommentParams(object):
    def __init__(self, fumen_id, comment_id, difficulty, comment, is_ok):
        self.fumen_id = fumen_id
        self.comment_id = comment_id
        self.difficulty = difficulty
        self.comment = comment
        self.is_ok = is_ok


class DeleteFumenCommentParams(object):
    def __init__(self, comment_id, fumen_id, difficulty):
        self.comment_id = comment_id
        self.fumen_id = fumen_id
        self.difficulty = difficulty