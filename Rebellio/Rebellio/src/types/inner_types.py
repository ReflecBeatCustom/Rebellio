class ViewFumenCommentParams(object):
    def __init__(self, comment_id):
        self.comment_id = comment_id

class DeleteAbsurdRecordParams(object):
    def __init__(self, fumen_id, user_name, score):
        self.fumen_id = fumen_id
        self.user_name = user_name
        self.score = score