from datetime import datetime
from typing import Callable, Awaitable, Dict, Any

from aiogram import BaseMiddleware
from aiogram.types import TelegramObject, Chat
from services.statistics_service import StatisticsService


class ChatEventsMiddleware(BaseMiddleware):

    async def __call__(
            self,
            handler: Callable[[TelegramObject, Dict[str, Any]], Awaitable[Any]],
            event: TelegramObject,
            data: Dict[str, Any],
    ) -> Any:

        chat: Chat = data.get('event_chat')
        if chat is None:
            return await handler(event, data)

        statistics_service: StatisticsService = data.get('statistics_service')

        await statistics_service.save_event(chat.id, datetime.now().date())
        return await handler(event, data)
