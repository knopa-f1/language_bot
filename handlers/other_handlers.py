import logging

from aiogram import Router
from aiogram.types import Message

from services.base_service import Context

logger = logging.getLogger(__name__)

router = Router()


# any commands, except "/start" и "/help"
@router.message()
async def send_message(message: Message, context: Context):
    await message.reply(text=context.i18n.no.answer())  # type: ignore[union-attr]
