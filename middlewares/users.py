from typing import Callable, Awaitable, Dict, Any, cast

from aiogram import BaseMiddleware
from aiogram.types import TelegramObject, Message, User, Chat

from servises.chat_interection_service import ChatInteractionService
from sqlalchemy.ext.asyncio import AsyncSession


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

        chat_interaction_service: ChatInteractionService = data.get('chat_interaction_service')

        if not await chat_interaction_service.user_exist(user.id, chat.id):
            await chat_interaction_service.set_user(user, chat.id)
        return await handler(event, data)
