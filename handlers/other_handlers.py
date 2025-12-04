import logging

from aiogram import Router
from aiogram.types import Message

from services.context.request_context import RequestContext

logger = logging.getLogger(__name__)

router = Router()


# any commands, except "/start" и "/help"
@router.message()
async def send_message(message: Message, request_context: RequestContext):
    await message.reply(text=request_context.i18n.no.answer())  # type: ignore[union-attr]
