import logging
from collections import defaultdict
from dataclasses import dataclass, field

logger = logging.getLogger(__name__)

@dataclass
class UserCache:

    users_settings: dict = field(default_factory=defaultdict)

    def set(self, user_id, **kwargs):
        if self.users_settings.get(user_id, None) is None:
            self.users_settings[user_id] = {}
        for key, value in kwargs.items():
            self.users_settings[user_id][key] = value

    def get(self, user_id, key):
        if self.users_settings.get(user_id, None) is None:
            return None
        return self.users_settings[user_id].get(key, None)
