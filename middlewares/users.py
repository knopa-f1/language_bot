from typing import Callable, Awaitable, Dict, Any

from aiogram import BaseMiddleware
from aiogram.types import TelegramObject, User, Chat

from services.user_chat_service import UserChatService


class TrackAllUsersMiddleware(BaseMiddleware):

    async def __call__(
            self,
            handler: Callable[[TelegramObject, Dict[str, Any]], Awaitable[Any]],
            event: TelegramObject,
            data: Dict[str, Any],
    ) -> Any:

        user: User = data.get('event_from_user')
        chat: Chat = data.get('event_chat')
        if user is None:
            return await handler(event, data)

        user_chat_service: UserChatService = data.get('user_chat_service')

        if not await user_chat_service.user_exist(user.id, chat.id):
            await user_chat_service.set_user(user, chat.id)
        return await handler(event, data)
