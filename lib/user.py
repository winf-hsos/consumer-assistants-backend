from lib.logging import log_debug, DEBUG, INFO, ERROR


class User:
    def __init__(self, user_id):
        log_debug(f"Creating user {user_id}")
        self.user_id = user_id
        self.language = "german"

    def to_json(self):
        return {
            "user_id": self.user_id,
            "language": self.language
        }