from aiogram import Router
from aiogram.types import Message
from fluentogram import TranslatorRunner
import logging

from servises.chat_interection_service import ChatInteractionService

logger = logging.getLogger(__name__)

router = Router()


# any commands, except "/start" и "/help"
@router.message()
async def send_message(message: Message, chat_interaction_service: ChatInteractionService):
    await message.reply(text=chat_interaction_service.i18n.no.answer())
