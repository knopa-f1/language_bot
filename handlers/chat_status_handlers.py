import logging

from aiogram import Router, F, exceptions, types
from aiogram.filters import Command, CommandStart, ChatMemberUpdatedFilter, KICKED, MEMBER, IS_NOT_MEMBER
from aiogram.types import (Message, CallbackQuery, ChatMemberUpdated)
from servises.chat_interection_service import ChatInteractionService

logger = logging.getLogger(__name__)

# router initialization
router = Router()


@router.my_chat_member(ChatMemberUpdatedFilter(member_status_changed=KICKED))
async def user_blocked_bot(event: ChatMemberUpdated, chat_interaction_service: ChatInteractionService):
    print(event)
    await chat_interaction_service.set_chat_settings(event.chat, blocked_bot=True)


@router.my_chat_member(ChatMemberUpdatedFilter(member_status_changed=MEMBER))
async def user_unblocked_bot(event: ChatMemberUpdated, chat_interaction_service: ChatInteractionService):
    print(event)
    await chat_interaction_service.set_chat_settings(event.chat, blocked_bot=False)

