class GetPacksParams(object):
    def __init__(self, keyword, category):
        self.keyword = keyword
        self.category = category


class GetPackParams(object):
    def __init__(self, pack_id, category, is_show_all_pack_comments):
        self.pack_id = pack_id
        self.category = category
        self.is_show_all_pack_comments = is_show_all_pack_comments


class CreatePackCommentParams(object):
    def __init__(self, pack_id, comment):
        self.pack_id = pack_id
        self.comment = comment


class UpdatePackCommentParams(object):
    def __init__(self, pack_id, comment_id, comment):
        self.pack_id = pack_id
        self.comment_id = comment_id
        self.comment = comment


class DeletePackCommentParams(object):
    def __init__(self, pack_id, comment_id):
        self.pack_id = pack_id
        self.comment_id = comment_id


class GetPacksResponse(object):
    def __init__(self, get_packs_params, packs, pagination_info):
        self.get_packs_params = get_packs_params
        self.packs = packs
        self.pagination_info = pagination_info


class GetPackResponse(object):
    def __init__(self, get_pack_params, pack, pack_comments):
        self.get_pack_params = get_pack_params
        self.pack = pack
        self.pack_comments = pack_comments
