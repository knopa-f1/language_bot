from aiogram import Bot
from datetime import datetime

from database.database import Database
from keyboards.inline_keyboards import Keyboards
from fluentogram import TranslatorHub
from servises.users_service import UsersService
from sqlalchemy.ext.asyncio import async_sessionmaker
import logging

logger = logging.getLogger(__name__)


async def job_send_messages_to_users(bot: Bot,
                                     translator_hub: TranslatorHub,
                                     session_pool: async_sessionmaker):
    async with session_pool() as session:
        user_service = UsersService(session=session)
        users_list = await user_service.users_list_to_send(datetime.now().hour)

    for user_data in users_list:
        i18n = translator_hub.get_translator_by_locale(locale=user_data.lang)
        await bot.send_message(user_data.user_id, i18n.schedule.message(),
                               reply_markup=Keyboards.learn_keyboard(i18n))
