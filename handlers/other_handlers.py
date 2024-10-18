from aiogram import Router
from aiogram.types import Message
from fluentogram import TranslatorRunner

# Инициализируем роутер уровня модуля
router = Router()

# Этот хэндлер будет срабатывать на любые ваши сообщения,
# кроме команд "/start" и "/help"
@router.message()
async def send_message(message: Message, i18n: TranslatorRunner):
    await message.reply(text=i18n.no.answer())




