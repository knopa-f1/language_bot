import logging
from typing import Any, Awaitable, Callable, Dict

from aiogram import BaseMiddleware
from aiogram.types import Chat, TelegramObject, User

logger = logging.getLogger(__name__)


class TrackAllUsersMiddleware(BaseMiddleware):
    async def __call__(
        self,
        handler: Callable[[TelegramObject, Dict[str, Any]], Awaitable[Any]],
        event: TelegramObject,
        data: Dict[str, Any],
    ) -> Any:
        user: User = data.get("event_from_user")
        chat: Chat = data.get("event_chat")
        if user is None:
            return await handler(event, data)

        user_chat_service = data.get("user_chat_service")
        if user_chat_service is None:
            logger.error("user_chat_service is missing in middleware data")
        else:
            if not await user_chat_service.user_exists(user.id, chat.id):
                await user_chat_service.set_user(user, chat.id)
        return await handler(event, data)
