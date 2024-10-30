import logging
from typing import Any, Awaitable, Callable, Dict

from aiogram import BaseMiddleware
from aiogram.types import TelegramObject, Chat, User
from fluentogram import TranslatorHub
from keyboards.set_menu import set_main_menu
from servises.buttons_services import get_selected_data
from servises.chat_interection_service import ChatInteractionService

logger = logging.getLogger(__name__)


class TranslatorRunnerMiddleware(BaseMiddleware):
    async def __call__(
            self,
            handler: Callable[[TelegramObject, Dict[str, Any]], Awaitable[Any]],
            event: TelegramObject,
            data: Dict[str, Any]
    ) -> Any:

        chat: Chat = data.get('event_chat')
        user: User = data.get('event_from_user')
        if user is None:
            return await handler(event, data)

        chat_interaction_service: ChatInteractionService = data.get('chat_interaction_service')
        # maybe we changed the language, should try to check it
        reset_menu = False

        callback_query = event.callback_query
        if callback_query is not None and callback_query.data.startswith("button-language"):
            lang = get_selected_data(callback_query.data)
            reset_menu = True
        else:
            lang = await chat_interaction_service.get_chat_settings(chat.id, "lang")
            if lang is None:
                lang = user.language_code
        hub: TranslatorHub = data.get('_translator_hub')
        i18n = hub.get_translator_by_locale(locale=lang)
        data['chat_interaction_service'].i18n = i18n
        data['chat_interaction_service'].lang = lang

        # if reset_menu:
        #     await set_main_menu(event.bot, i18n)

        return await handler(event, data)
