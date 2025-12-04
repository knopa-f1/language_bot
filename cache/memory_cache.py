import logging

from cachetools import TTLCache

logger = logging.getLogger(__name__)


class MemoryCache:
    def __init__(self, maxsize=1000, ttl: int = 3600):
        self.chats_settings: TTLCache = TTLCache(maxsize=maxsize, ttl=ttl)
        self.users: TTLCache = TTLCache(maxsize=maxsize, ttl=ttl)

    async def set_chat_settings(self, chat_id: int, **kwargs):
        if self.chats_settings.get(chat_id, None) is None:
            self.chats_settings[chat_id] = {}
        for key, value in kwargs.items():
            self.chats_settings[chat_id][key] = value

    async def get_chat_settings(self, chat_id: int, key: str):
        if self.chats_settings.get(chat_id, None) is None:
            return None
        return self.chats_settings[chat_id].get(key, None)

    async def set_user(self, user_id: int, chat_id: int):
        self.users["user_id"] = chat_id

    async def user_exists(self, user_id: int):
        return self.users.get("user_id", None) is not None
