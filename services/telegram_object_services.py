from datetime import datetime

from aiogram.types import Chat, User
from db import ChatInfo


def get_chat_info(chat: Chat):
    chat_info = {atr: getattr(chat, atr, None) for atr in ChatInfo.props()}
    chat_info['start_date'] = datetime.now()
    return chat_info


def get_user_info(user: User):
    return {atr: getattr(user, atr, None) for atr in User.props()}
