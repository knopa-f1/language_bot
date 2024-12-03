from dataclasses import asdict

from db import User
from db.models import Chat
from db.requests.chats_requests import get_chat, upsert_chat, upsert_chat_info
from db.requests.users_requests import get_user, upsert_user
from services.base_service import BaseService
from services.telegram_object_services import get_user_info, get_chat_info

from aiogram.types import Chat as TChat
from aiogram.types import User as TUser


class UserChatService(BaseService):

    async def user_exist(self,
                         user_id: int,
                         chat_id: int
                         ) -> int | str | None:
        user_exist = self.cache.user_exist(user_id)
        if not user_exist:
            user: User | None = await get_user(self.session, user_id, chat_id)
            if user is not None:
                user_exist = True
                self.cache.set_user(user_id, chat_id)
        return user_exist

    async def set_user(self, user: TUser, chat_id: int):
        self.cache.set_user(user.id, chat_id)
        await upsert_user(self.session,
                          user.id,
                          chat_id,
                          get_user_info(user))

    async def chat_settings_exists(self,
                                   chat_id: int) -> bool:
        return False if await get_chat(self.session, chat_id) is None else True

    async def get_chat_settings(self,
                                chat_id: int,
                                name: str = "lang"
                                ) -> int | str | None:
        value = self.cache.get_chat_settings(chat_id, name)
        if value is None:
            chat: Chat | None = await get_chat(self.session, chat_id)
            if chat is not None:
                value = getattr(chat, name)
                self.cache.set_chat_settings(chat_id, **{name: value})
        return value

    async def set_chat_settings(self, chat: TChat, **kwargs) -> None:
        self.cache.set_chat_settings(chat.id, **kwargs)
        await upsert_chat(self.session,
                          chat.id,
                          get_chat_info(chat),
                          asdict(self.default_settings.chat_set),
                          **kwargs)

    async def get_chat_settings_description(self, chat_id: int) -> str:
        chat: [Chat, None] = await get_chat(self.session, chat_id)
        if chat is None:
            return self.i18n.error.no.settings()
        else:
            return self.i18n.settings.desctiption(**chat.attributes_dict)

    async def set_chat_info(self, chat: TChat, **kwargs) -> None:
        await upsert_chat_info(self.session,
                               chat.id,
                               **kwargs)
