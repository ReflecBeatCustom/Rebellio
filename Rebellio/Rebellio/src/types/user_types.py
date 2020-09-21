class GetUserDetailParams(object):
    def __init__(self, user_name):
        self.user_name = user_name


class GetUserDetailResponse(object):
    def __init__(self, user, recent_records, high_records):
        self.user = user
        self.recent_records = recent_records
        self.high_records = high_records