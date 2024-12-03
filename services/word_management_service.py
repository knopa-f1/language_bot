import random
from typing import Type

from db import Word
from db.models import Status
from db.requests.statistics_requests import should_del_current_word, change_word_status
from db.requests.words_requests import delete_random_current_words, add_current_chat_words, delete_current_word, \
    current_words_exists, get_words, get_word_by_id
from keyboards.inline_keyboards import Keyboards
from services.base_service import BaseService

from aiogram.types import Chat as TChat


class WordManagementService(BaseService):

    def __init__(self, context, user_chat_service):
        super().__init__(context)
        self.user_chat_service = user_chat_service

    async def set_count_current_words(self, chat: TChat, count_current: int) -> None:
        last_count_current = await self.user_chat_service.get_chat_settings(chat.id, "count_current")
        if last_count_current == count_current:
            return
        elif last_count_current > count_current:
            await delete_random_current_words(self.session, chat.id, last_count_current - count_current)
        else:
            await add_current_chat_words(self.session, chat.id, self.default_settings.answer_set.repeat_after_days,
                                         count_current - last_count_current)
        await self.user_chat_service.set_chat_settings(chat, count_current=count_current)

    async def add_current_words(self, chat_id: int, count: int = None) -> None:
        if count is None:
            count: int = await self.user_chat_service.get_chat_settings(chat_id, "count_current")
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
        """return words - 1 from current_words, else - from word's dictionary"""

        if not await current_words_exists(self.session, chat_id):
            await self.add_current_words(chat_id)

        return await get_words(self.session, chat_id, count)

    async def get_word_by_id(self,
                             word_id: int
                             ) -> Type[Word] | None:
        return await get_word_by_id(self.session, word_id)

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

        return {
            "message_text": message_text,
            "keyboard": keyboard
        }
