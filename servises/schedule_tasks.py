from aiogram import  Bot
from database.database import bot_database
from datetime import datetime
from keyboards.inline_keyboards import learn_keyboard
from lexicon.lexicon import LEXICON_RU

async def job_send_messages_to_users(bot: Bot):
    # Список пользователей, кому надо сейчас отправить сообщение
    users_list = bot_database.users_settings.users_list_to_send(datetime.now().hour)
    text = LEXICON_RU["schedule_message"]
    keyboard = learn_keyboard()
    [await bot.send_message(user_id[0], text, reply_markup=keyboard) for user_id in users_list]



