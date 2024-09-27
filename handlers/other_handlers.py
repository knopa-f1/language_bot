from aiogram import Router
from aiogram.types import Message
from lexicon.lexicon import LEXICON_RU
import requests

# Инициализируем роутер уровня модуля
router = Router()

# Этот хэндлер будет срабатывать на любые ваши сообщения,
# кроме команд "/start" и "/help"
@router.message()
async def send_message(message: Message):
    await message.reply(text=LEXICON_RU['no_answer'])




