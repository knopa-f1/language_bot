from dataclasses import asdict

from aiogram.types import Chat as TChat
from aiogram.types import User as TUser

from db import User
from db.models import Chat
from db.repositories.chats import ChatsRepository
from db.repositories.users import UsersRepository
from services.base_service import BaseService
from services.telegram_object_services import get_chat_info, get_user_info


class UserChatService(BaseService):
    def __init__(
        self,
        context,
        chats_repo: ChatsRepository,
        users_repo: UsersRepository,
    ):
        super().__init__(context)
        self.chats_repo = chats_repo
        self.users_repo = users_repo

    async def user_exists(self, user_id: int, chat_id: int) -> int | str | None:
        user_exist = self.cache.user_exists(
            user_id,
        )
        if not user_exist:
            user: User | None = await self.users_repo.get_user(user_id, chat_id)
            if user is not None:
                user_exist = True
                self.cache.set_user(user_id, chat_id)
        return user_exist

    async def set_user(self, user: TUser, chat_id: int):
        self.cache.set_user(user.id, chat_id)
        await self.users_repo.upsert_user(user.id, chat_id, get_user_info(user))

    async def chat_settings_exists(self, chat_id: int) -> bool:
        return False if await self.chats_repo.get_chat(chat_id) is None else True

    async def get_chat_settings(self, chat_id: int, name: str = "lang") -> int | str | None:
        value = self.cache.get_chat_settings(chat_id, name)
        if value is None:
            chat: Chat | None = await self.chats_repo.get_chat(chat_id)
            if chat is not None:
                value = getattr(chat, name)
                self.cache.set_chat_settings(chat_id, **{name: value})
        return value

    async def set_chat_settings(self, chat: TChat, **kwargs) -> None:
        self.cache.set_chat_settings(chat.id, **kwargs)
        await self.chats_repo.upsert_chat(
            chat.id,
            get_chat_info(chat),
            asdict(self.default_settings.chat_set),
            **kwargs,
        )

    async def get_chat_settings_description(self, chat_id: int) -> str:
        chat: Chat | None = await self.chats_repo.get_chat(chat_id)
        if chat is None:
            return self.i18n.error.no.settings()
        else:
            return self.i18n.settings.desctiption(**chat.attributes_dict)

    async def set_chat_info(self, chat: TChat, **kwargs) -> None:
        await self.chats_repo.upsert_chat_info(chat.id, **kwargs)
