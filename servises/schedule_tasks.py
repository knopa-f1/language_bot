from aiogram import  Bot
from database.database import bot_settings
from datetime import datetime

async def job_send_messages_to_users(bot: Bot):
    # Список пользователей, кому надо сейчас отправить сообщение
    users_list = bot_settings.users_list_to_send(datetime.now().hour)
    text = bot_settings.get_random_word()
    [await bot.send_message(int(user_id), text) for user_id in users_list]



