import asyncio

from aiogram import Bot
from datetime import datetime

from keyboards.inline_keyboards import Keyboards
from fluentogram import TranslatorHub
from services.reminder_service import ReminderService
from sqlalchemy.ext.asyncio import async_sessionmaker
import logging

logger = logging.getLogger(__name__)


async def send_reminder(chat_data,
                        bot: Bot,
                        translator_hub: TranslatorHub):
    i18n = translator_hub.get_translator_by_locale(locale=chat_data.lang)
    try:
        await bot.send_message(chat_data.chat_id, i18n.schedule.message(),
                               reply_markup=Keyboards.reminder_keyboard(i18n))
        logger.info(f"Sent reminder to chat {chat_data.chat_id}")
    except Exception as e:
        logger.error(f"Error in sending reminder to chat {chat_data.chat_id}:{e}")


async def job_send_messages_to_users(bot: Bot,
                                     translator_hub: TranslatorHub,
                                     session_pool: async_sessionmaker):
    logger.info(f"Start send_reminder")
    async with session_pool() as session:
        reminder_service = ReminderService(session=session)
        chat_list = await reminder_service.chats_list_to_send(datetime.now().hour)

    tasks = []
    for chat_data in chat_list:
        task = send_reminder(chat_data, bot, translator_hub)
        tasks.append(task)

    await asyncio.gather(*tasks)
    logger.info(f"End send_reminder")
