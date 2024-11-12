import random
from dataclasses import dataclass, asdict
from datetime import datetime
from typing import Type

from aiogram.types import Chat as TChat
from aiogram.types import User as TUser

from cache.cache import Cache
from config_data.constants import DefaultSettings
from db import User
from db.models import Word, Status, Chat, ChatInfo
from db.requests.statistics_requests import get_chat_statistic, save_statistic_by_word, should_del_current_word, \
    change_word_status
from db.requests.chats_requests import get_chat, upsert_chat, get_chats_to_reminder, upsert_chat_info
from db.requests.users_requests import upsert_user, get_user
from db.requests.words_requests import add_current_chat_words, delete_current_word, current_words_exists, \
    get_words, get_word_by_id, delete_random_current_words
from fluentogram import TranslatorRunner
from keyboards.inline_keyboards import Keyboards
from sqlalchemy.ext.asyncio import AsyncSession
import logging

logger = logging.getLogger(__name__)


@dataclass
class ChatInteractionService:
    session: AsyncSession
    cache: Cache | None = None
    i18n: TranslatorRunner | None = None
    default_settings: DefaultSettings | None = None
    lang: str = ""

    @staticmethod
    def get_chat_info(chat: TChat):
        chat_info = {atr: getattr(chat, atr, None) for atr in ChatInfo.props()}
        chat_info['start_date'] = datetime.now()
        return chat_info

    @staticmethod
    def get_user_info(user: TUser):
        return {atr: getattr(user, atr, None) for atr in User.props()}

    async def user_exist(self,
                         user_id: int,
                         chat_id: int
                         ) -> int | str | None:
        user_exist = self.cache.user_exist(user_id, chat_id)
        if not user_exist:
            user: User | None = await get_user(self.session, user_id, chat_id)
            if user is not None:
                user_exist = True
                self.cache.set_user(user_id, chat_id)
        return user_exist

    async def set_user(self, user: TUser, chat_id: int):
        self.cache.set_user(user.id, chat_id)
        await upsert_user(self.session,
                          user.id,
                          chat_id,
                          ChatInteractionService.get_user_info(user))

    async def chat_settings_exists(self,
                                   chat_id: int) -> bool:
        return False if await get_chat(self.session, chat_id) is None else True

    async def get_chat_settings(self,
                                chat_id: int,
                                name: str = "lang"
                                ) -> int | str | None:
        value = self.cache.get_chat_settings(chat_id, name)
        if value is None:
            chat: Chat | None = await get_chat(self.session, chat_id)
            if chat is not None:
                value = getattr(chat, name)
                self.cache.set_chat_settings(chat_id, **{name: value})
        return value

    async def set_chat_settings(self, chat: TChat, **kwargs) -> None:
        self.cache.set_chat_settings(chat.id, **kwargs)
        await upsert_chat(self.session,
                          chat.id,
                          ChatInteractionService.get_chat_info(chat),
                          asdict(self.default_settings.chat_set),
                          **kwargs)

    async def get_chat_settings_description(self, chat_id: int) -> str:
        chat: [Chat, None] = await get_chat(self.session, chat_id)
        if chat is None:
            return self.i18n.error.no.settings()
        else:
            return self.i18n.settings.desctiption(**chat.attributes_dict)

    async def set_chat_info(self, chat: TChat, **kwargs) -> None:
        await upsert_chat_info(self.session,
                               chat.id,
                               **kwargs)

    async def set_count_current_words(self, chat: TChat, count_current: int) -> None:
        last_count_current = await self.get_chat_settings(chat.id, "count_current")
        if last_count_current == count_current:
            return
        elif last_count_current > count_current:
            print(f'delete_random_current_words {last_count_current - count_current}')
            await delete_random_current_words(self.session, chat.id, last_count_current - count_current)
        else:
            print(f'add_current_chat_words {count_current - last_count_current}')
            await add_current_chat_words(self.session, chat.id, self.default_settings.answer_set.repeat_after_days,
                                         count_current - last_count_current)
        await self.set_chat_settings(chat, count_current=count_current)

    async def chats_list_to_send(self, current_hour: int) -> list:
        "Should we send the reminder to chats"
        return await get_chats_to_reminder(self.session, current_hour)

    async def add_current_words(self, chat_id: int, count: int = None) -> None:
        if count is None:
            count: int = await self.get_chat_settings(chat_id, "count_current")
        repeat_after_days = self.default_settings.answer_set.repeat_after_days

        await add_current_chat_words(self.session, chat_id, repeat_after_days, count)

    async def update_current_words(self,
                                   chat_id: int,
                                   word_id: int,
                                   del_word: bool = False,
                                   already_know: bool = False) -> None:
        if del_word:
            status = Status.already_know if already_know else Status.never_learn
        elif await should_del_current_word(self.session,
                                           chat_id,
                                           word_id,
                                           self.default_settings.answer_set.count_correct,
                                           self.default_settings.answer_set.percent_correct):
            status = Status.learned
        else:
            return

        await delete_current_word(self.session, chat_id, word_id)

        await self.add_current_words(chat_id, count=1)
        await change_word_status(self.session, chat_id, word_id, status)

    async def mark_word_as_never_learn(self,
                                       chat_id: int,
                                       word_id: int
                                       ):
        await self.update_current_words(chat_id, word_id, True)

    async def mark_word_as_already_know(self,
                                        chat_id: int,
                                        word_id: int
                                        ):
        await self.update_current_words(chat_id, word_id, True, True)

    async def get_words_to_learn(self,
                                 chat_id: int,
                                 count: int = 3
                                 ) -> dict:
        "return words - 1 from current_words, else - from word's dictionary"

        if not await current_words_exists(self.session, chat_id):
            await self.add_current_words(chat_id)

        return await get_words(self.session, chat_id, count)

    async def get_word_by_id(self,
                             word_id: int
                             ) -> Type[Word] | None:
        return await get_word_by_id(self.session, word_id)

    async def get_statistics_description(self,
                                         chat_id: int
                                         ) -> str:
        chat_stat: None | dict = await get_chat_statistic(self.session, chat_id)
        if chat_stat is None:
            return self.i18n.error.no.stat()
        else:
            return self.i18n.stat.description(**chat_stat)

    async def save_statistic(self,
                             chat_id: int,
                             word_id: int,
                             correct: int = 0,
                             wrong: int = 0):
        await save_statistic_by_word(self.session, chat_id, word_id, correct, wrong)
        await self.update_current_words(chat_id, word_id)

    async def prepare_words_to_learn(self,
                                     chat_id: int,
                                     answer_text: str = "") -> dict:

        words = await self.get_words_to_learn(chat_id)
        words_list = words["variants"]
        words_list.append(words["correct_word"])

        type_id = random.randint(1, 2)  # type - 1 - find translate to word, 2 - word by translate
        word = words["correct_word"].word if type_id == 1 else getattr(words["correct_word"],
                                                                       f"translation_{self.lang}")
        answer_id = words["correct_word"].word_id
        message_text = (f'{answer_text}\n\n'
                        f'<b>{word}</b>\n\n'
                        f'{self.i18n.get(f'message-text-{type_id}')}')
        random.shuffle(words_list)

        keyboard = Keyboards.guess_word_keyboard(self.i18n, words_list, type_id, answer_id, self.lang)

        return {"message_text": message_text,
                "keyboard": keyboard}
