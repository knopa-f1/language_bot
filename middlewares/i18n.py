import logging
from typing import Any, Awaitable, Callable, Dict

from aiogram import BaseMiddleware
from aiogram.types import TelegramObject, User
from fluentogram import TranslatorHub
from keyboards.set_menu import set_main_menu
from servises.buttons_services import get_selected_data
from servises.users_service import UsersService

logger = logging.getLogger(__name__)


class TranslatorRunnerMiddleware(BaseMiddleware):
    async def __call__(
            self,
            handler: Callable[[TelegramObject, Dict[str, Any]], Awaitable[Any]],
            event: TelegramObject,
            data: Dict[str, Any]
    ) -> Any:

        user: User = data.get('event_from_user')
        if user is None:
            return await handler(event, data)

        user_service: UsersService = data.get('user_service')
        # maybe we changed the language, should try to check it
        reset_menu = False

        callback_query = event.callback_query
        if callback_query is not None and callback_query.data.startswith("button-language"):
            lang = get_selected_data(callback_query.data)
            reset_menu = True
        else:
            lang = await user_service.get_user_settings(user.id, "lang")
            if lang is None:
                lang = user.language_code
        hub: TranslatorHub = data.get('_translator_hub')
        i18n = hub.get_translator_by_locale(locale=lang)
        data['user_service'].i18n = i18n
        data['user_service'].lang = lang

        if reset_menu:
            await set_main_menu(event.bot, i18n)

        return await handler(event, data)
