import logging
from typing import Any, Awaitable, Callable, Dict

from aiogram import BaseMiddleware
from aiogram.dispatcher.event.handler import HandlerObject
from aiogram.types import TelegramObject, User
from fluentogram import TranslatorHub
from servises.servises import get_selected_data
from servises.user_settings import UserSettings

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

        # возможно, мы сменили язык в этом событии, попробуем получить его оттуда
        callback_query = event.callback_query
        if callback_query is not None and callback_query.data.startswith("button-language_"):
            lang = get_selected_data(callback_query.data, "button-language_")
        else:
            # если нет, посмотрим в кэше и БД, если уж и там нет - из параметра сообщения
            bot_database = data.get('bot_database')
            users_cache = data.get('users_cache')
            default_settings = data.get('default_settings')
            lang = UserSettings.get(user.id, bot_database, users_cache, "lang")
            if lang is None:
                UserSettings.set(user.id, bot_database, users_cache, default_settings, lang=user.language_code)
                lang = user.language_code

        hub: TranslatorHub = data.get('_translator_hub')
        data['i18n'] = hub.get_translator_by_locale(locale=lang)
        data['lang'] = lang

        return await handler(event, data)
