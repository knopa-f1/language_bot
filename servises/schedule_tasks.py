from aiogram import Bot
from datetime import datetime

from database.database import Database
from keyboards.inline_keyboards import Keyboards
from fluentogram import TranslatorHub
from servises.chat_interection_service import ChatInteractionService
from sqlalchemy.ext.asyncio import async_sessionmaker
import logging

logger = logging.getLogger(__name__)


async def job_send_messages_to_users(bot: Bot,
                                     translator_hub: TranslatorHub,
                                     session_pool: async_sessionmaker):
    async with session_pool() as session:
        chat_interaction_service = ChatInteractionService(session=session)
        chat_list = await chat_interaction_service.chats_list_to_send(datetime.now().hour)

    for chat_data in chat_list:
        i18n = translator_hub.get_translator_by_locale(locale=chat_data.lang)
        await bot.send_message(chat_data.chat_id, i18n.schedule.message(),
                               reply_markup=Keyboards.learn_keyboard(i18n))
