import logging

from aiogram import Router
from aiogram.filters import KICKED, MEMBER, ChatMemberUpdatedFilter
from aiogram.types import ChatMemberUpdated

from services.user_chat_service import UserChatService

logger = logging.getLogger(__name__)

# router initialization
router = Router()


@router.my_chat_member(ChatMemberUpdatedFilter(member_status_changed=KICKED))
async def user_blocked_bot(event: ChatMemberUpdated, user_chat_service: UserChatService):
    print(event)
    await user_chat_service.set_chat_settings(event.chat, blocked_bot=True)


@router.my_chat_member(ChatMemberUpdatedFilter(member_status_changed=MEMBER))
async def user_unblocked_bot(event: ChatMemberUpdated, user_chat_service: UserChatService):
    print(event)
    await user_chat_service.set_chat_settings(event.chat, blocked_bot=False)
