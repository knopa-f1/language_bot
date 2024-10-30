import logging
from collections import defaultdict
from dataclasses import dataclass, field

logger = logging.getLogger(__name__)


@dataclass
class Cache:
    chats_settings: dict = field(default_factory=defaultdict)
    users: set[tuple] = field(default_factory=set)

    def set_chat_settings(self, chat_id: int, **kwargs):
        if self.chats_settings.get(chat_id, None) is None:
            self.chats_settings[chat_id] = {}
        for key, value in kwargs.items():
            self.chats_settings[chat_id][key] = value

    def get_chat_settings(self, chat_id: int, key: str):
        if self.chats_settings.get(chat_id, None) is None:
            return None
        return self.chats_settings[chat_id].get(key, None)

    def set_user(self, user_id: int, chat_id: int):
        self.users.add((user_id, chat_id))

    def user_exist(self, user_id: int, chat_id: int):
        return True if (user_id, chat_id) in self.users else False
