from aiogram import Bot
from datetime import datetime
from database.database import Database
from keyboards.inline_keyboards import Keyboards
from fluentogram import TranslatorHub


async def job_send_messages_to_users(bot: Bot,
                                     translator_hub: TranslatorHub,
                                     bot_database: Database):
    # Список пользователей, кому надо сейчас отправить сообщение
    users_list = bot_database.users_settings.users_list_to_send(datetime.now().hour)
    for user_data in users_list:
        i18n = translator_hub.get_translator_by_locale(locale=user_data["lang"])
        await bot.send_message(user_data["user_id"], i18n.schedule.message(),
                               reply_markup=Keyboards.learn_keyboard(i18n))
