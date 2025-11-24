import logging
from datetime import datetime
from typing import Any, Awaitable, Callable, Dict

from aiogram import BaseMiddleware
from aiogram.types import Chat, TelegramObject

logger = logging.getLogger(__name__)


class ChatEventsMiddleware(BaseMiddleware):
    async def __call__(
        self,
        handler: Callable[[TelegramObject, Dict[str, Any]], Awaitable[Any]],
        event: TelegramObject,
        data: Dict[str, Any],
    ) -> Any:
        chat: Chat = data.get("event_chat")
        if chat is None:
            return await handler(event, data)

        statistics_service = data.get("statistics_service")
        if statistics_service is None:
            logger.error("statistics_service is missing in middleware data")
        else:
            await statistics_service.save_event(chat.id, datetime.now().date())
        return await handler(event, data)
