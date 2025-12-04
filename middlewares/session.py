import logging
from typing import Any, Awaitable, Callable, Dict

from aiogram import BaseMiddleware
from aiogram.types import TelegramObject

from services.context.request_context import RequestContext

logger = logging.getLogger(__name__)


class DbSessionMiddleware(BaseMiddleware):
    async def __call__(
        self,
        handler: Callable[[TelegramObject, Dict[str, Any]], Awaitable[Any]],
        event: TelegramObject,
        data: Dict[str, Any],
    ) -> Any:
        global_context = data["global_context"]

        async with global_context.session_pool() as session:
            request_context = RequestContext(session)
            data["request_context"] = request_context

            return await handler(event, data)
