from typing import Callable, Awaitable, Dict, Any

from aiogram import BaseMiddleware
from aiogram.types import TelegramObject
from servises.chat_interection_service import ChatInteractionService
from sqlalchemy.ext.asyncio import async_sessionmaker
import logging

logger = logging.getLogger(__name__)


class DbSessionMiddleware(BaseMiddleware):
    def __init__(self, session_pool: async_sessionmaker):
        super().__init__()
        self.session_pool = session_pool

    async def __call__(
            self,
            handler: Callable[[TelegramObject, Dict[str, Any]], Awaitable[Any]],
            event: TelegramObject,
            data: Dict[str, Any],
    ) -> Any:
        async with self.session_pool() as session:
            data["chat_interaction_service"] = ChatInteractionService(
                session=session,
                cache=data.get('cache'),
                default_settings=data.get('default_settings')
            )
            return await handler(event, data)
