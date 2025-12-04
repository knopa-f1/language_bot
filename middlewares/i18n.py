import logging
from typing import Any, Awaitable, Callable, Dict

from aiogram import BaseMiddleware
from aiogram.types import Chat, TelegramObject, User
from fluentogram import TranslatorHub

from services.buttons_services import get_selected_data

logger = logging.getLogger(__name__)


class TranslatorRunnerMiddleware(BaseMiddleware):
    async def __call__(
        self,
        handler: Callable[[TelegramObject, Dict[str, Any]], Awaitable[Any]],
        event: TelegramObject,
        data: Dict[str, Any],
    ) -> Any:
        chat: Chat = data.get("event_chat")
        user: User = data.get("event_from_user")
        if user is None:
            return await handler(event, data)

        global_context = data["global_context"]
        request_context = data["request_context"]
        if global_context is None:
            return await handler(event, data)
        factory = data["service_factory"]
        user_chat_service = factory.create_user_chat_service(request_context)

        callback_query = event.callback_query
        if callback_query is not None and callback_query.data.startswith("button-language"):
            lang = get_selected_data(callback_query.data)
            reset_menu = True
        else:
            lang_settings = await user_chat_service.get_chat_settings(chat.id, "lang")
            if lang_settings is None:
                lang = user.language_code
            else:
                lang = str(lang_settings)

        hub: TranslatorHub = global_context.translator_hub
        i18n = hub.get_translator_by_locale(locale=lang)

        data["user_chat_service"] = user_chat_service
        data["word_management_service"] = factory.create_word_management_service(request_context)
        data["statistics_service"] = factory.create_statistics_service(request_context)

        request_context.i18n = i18n
        request_context.lang = lang

        return await handler(event, data)
