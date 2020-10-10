class ViewFumenCommentParams(object):
    def __init__(self, comment_id):
        self.comment_id = comment_id

class DeleteAbsurdRecordParams(object):
    def __init__(self, fumen_id, user_name, score):
        self.fumen_id = fumen_id
        self.user_name = user_name
        self.score = score

class VoteOnSubdiffParams(object):
    def __init__(self, fumen_id, difficulty, subdiff):
        self.fumen_id = fumen_id
        self.difficulty = difficulty
        self.subdiff = subdiff

class GetSubdiffVotesResponse(object):
    def __init__(self, fumen_id, title, difficulty, level, avg_level, subdiff_votes, is_voted_by_user):
        self.fumen_id = fumen_id
        self.title = title
        self.difficulty = difficulty
        self.level = level
        self.avg_level = avg_level
        self.subdiff_votes = subdiff_votes
        self.is_voted_by_user = is_voted_by_user