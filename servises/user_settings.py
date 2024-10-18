from dataclasses import dataclass

from config_data.constants import DefaultSettings
from database.database import Database
from servises.users_cache import UsersCache


@dataclass
class UserSettings:

    @staticmethod
    def get(user_id,
            bot_database: Database,
            users_cache: UsersCache,
            name: str = "lang"):
        value = users_cache.get(user_id, name)
        if value is None:
            value = bot_database.users_settings.get(user_id, name)
            users_cache.set(user_id, **{name: value})
        return value

    @staticmethod
    def set(user_id,
            bot_database: Database,
            users_cache: UsersCache,
            default_settings: DefaultSettings,
            **kwargs):
        users_cache.set(user_id, **kwargs)
        bot_database.users_settings.set(user_id, default_settings, **kwargs)