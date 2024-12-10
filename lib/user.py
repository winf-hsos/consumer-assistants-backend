from lib.logging import log_debug, DEBUG, INFO, ERROR

class User:
    def __init__(self, user):
        log_debug(f"Creating user {user.get('user_id')}")
        self.user = user
        self.language = user.get("language")