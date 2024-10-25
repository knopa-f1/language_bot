import random
from dataclasses import dataclass, asdict
from typing import Union, Type

from cache.users_cache import UserCache
from config_data.constants import DefaultSettings
from db import Word
from db.models import User, Word, Status
from db.requests.statistics_requests import get_user_statistic, save_statistic_by_word, should_del_current_word, \
    change_word_status
from db.requests.users_requests import get_user, upsert_user, get_users_to_reminder
from db.requests.words_requests import add_current_user_words, delete_current_word, current_words_exists, \
    get_words, get_word_by_id
from fluentogram import TranslatorRunner
from keyboards.inline_keyboards import Keyboards
from sqlalchemy.ext.asyncio import AsyncSession
import logging

logger = logging.getLogger(__name__)


@dataclass
class UsersService:
    session: AsyncSession
    cache: UserCache | None = None
    i18n: TranslatorRunner | None = None
    default_settings: DefaultSettings | None = None
    lang: str = ""

    async def user_settings_exists(self,
                                   user_id: int) -> bool:
        return False if await get_user(self.session, user_id) is None else True

    async def get_user_settings(self,
                                user_id: int,
                                name: str = "lang"
                                ) -> int | str | None:
        value = self.cache.get(user_id, name)
        if value is None:
            user: User | None = await get_user(self.session, user_id)
            if user is not None:
                value = getattr(user, name)
                self.cache.set(user_id, **{name: value})
        return value

    async def set_user_settings(self, user_id: int, **kwargs):
        self.cache.set(user_id, **kwargs)
        await upsert_user(self.session,
                          user_id,
                          asdict(self.default_settings.user_set),
                          **kwargs)

    async def get_user_settings_description(self, user_id: int) -> str:
        user: [User, None] = await get_user(self.session, user_id)
        if user is None:
            return self.i18n.error.no.settings()
        else:
            return self.i18n.settings.desctiption(**user.attributes_dict)

    async def users_list_to_send(self, current_hour: int) -> list:
        "Should we send the reminder to user"
        return await get_users_to_reminder(self.session, current_hour)

    async def add_current_user_words(self, user_id: int, count: int = None) -> None:
        if count is None:
            count: int = self.default_settings.answer_set.count_current
        repeat_after_days = self.default_settings.answer_set.repeat_after_days

        await add_current_user_words(self.session, user_id, repeat_after_days, count)

    async def update_current_words(self,
                                   user_id: int,
                                   word_id: int,
                                   del_word: bool = False) -> None:
        if del_word:
            status = Status.never_learn
        elif await should_del_current_word(self.session,
                                           user_id,
                                           word_id,
                                           self.default_settings.answer_set.count_correct,
                                           self.default_settings.answer_set.percent_correct):
            status = Status.learned
        else:
            return

        await delete_current_word(self.session, user_id, word_id)

        await self.add_current_user_words(user_id, count=1)
        await change_word_status(self.session, user_id, word_id, status)

    async def mark_word_as_never_learn(self,
                                       user_id: int,
                                       word_id: int
                                       ):
        await self.update_current_words(user_id, word_id, True)

    async def get_words_to_learn(self,
                                 user_id: int,
                                 count: int = 3
                                 ) -> dict:
        "return words - 1 from current_words, else - from word's dictionary"

        if not await current_words_exists(self.session, user_id):
            await self.add_current_user_words(user_id)

        return await get_words(self.session, user_id, count)

    async def get_word_by_id(self,
                             word_id: int
                             ) -> Type[Word] | None:
        return await get_word_by_id(self.session, word_id)

    async def get_statistics_description(self,
                                         user_id: int
                                         ) -> str:
        user_stat: None | dict = await get_user_statistic(self.session, user_id)
        if user_stat is None:
            return self.i18n.error.no_stat()
        else:
            return self.i18n.stat.description(**user_stat)

    async def save_statistic(self,
                             user_id: int,
                             word_id: int,
                             correct: int = 0,
                             wrong: int = 0):
        await save_statistic_by_word(self.session, user_id, word_id, correct, wrong)
        await self.update_current_words(user_id, word_id)

    async def prepare_words_to_learn(self,
                                     user_id: int,
                                     answer_text: str = "") -> dict:

        words = await self.get_words_to_learn(user_id)
        words_list = words["variants"]
        words_list.append(words["correct_word"])

        type_id = random.randint(1, 2)  # type - 1 - find translate to word, 2 - word by translate
        word = words["correct_word"].word if type_id == 1 else getattr(words["correct_word"],
                                                                       f"translation_{self.lang}")
        answer_id = words["correct_word"].word_id
        message_text = (f'{answer_text}\n\n'
                        f'{word}\n\n'
                        f'{self.i18n.get(f'message-text-{type_id}')}')
        random.shuffle(words_list)

        keyboard = Keyboards.guess_word_keyboard(self.i18n, words_list, type_id, answer_id, self.lang)

        return {"message_text": message_text,
                "keyboard": keyboard}
