class SessionInfo(object):
    def __init__(self, is_login, user_name, user_access_level):
        self.is_login = is_login
        self.user_name = user_name
        self.user_access_level = user_access_level


class PaginationInfo(object):
    def __init__(self, start_page, page_size):
        self.start_page = start_page
        self.page_size = page_size
        self.total = 0
        self.pages = []
        self.total_page = 0
