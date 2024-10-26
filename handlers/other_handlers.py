from aiogram import Router
from aiogram.types import Message
from fluentogram import TranslatorRunner
import logging

logger = logging.getLogger(__name__)

router = Router()

# any commands, except "/start" и "/help"
@router.message()
async def send_message(message: Message, i18n: TranslatorRunner):
    await message.reply(text=i18n.no.answer())




