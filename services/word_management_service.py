import random
from typing import Type

from db import Word
from db.models import Status
from db.requests.statistics_requests import should_del_current_word, change_word_status
from db.requests.words_requests import delete_random_current_words, add_current_chat_words, delete_current_word, \
    current_words_exists, get_words, get_word_by_id
from keyboards.inline_keyboards import Keyboards
from services.base_service import BaseService

from aiogram.types import Chat as TChat, InlineKeyboardMarkup

from services.statistics_service import StatisticsService


class WordManagementService(BaseService):

    def __init__(self, context, user_chat_service):
        super().__init__(context)
        self.user_chat_service = user_chat_service

    def _letters_get_state(self, chat_id):
        return self.cache.get_chat_settings(chat_id, "letters_state")

    def _letters_set_state(self, chat_id, state):
        self.cache.set_chat_settings(chat_id, letters_state=state)

    def _letters_clear_state(self, chat_id):
        self.cache.set_chat_settings(chat_id, letters_state=None)

    @staticmethod
    def _shuffle_letters_with_positions(phrase):
        result = []
        word = []
        phrase_to_shuffle = phrase.lower().strip()
        separate_chars = ', .:'

        for i, char in enumerate(phrase_to_shuffle):
            if char in separate_chars:
                random.shuffle(word)
                result += word
                result.append((i, char))
                word = []
            else:
                word.append((i, char))
        if word:
            random.shuffle(word)
            result += word
        return result

    @staticmethod
    def _build_progress(target: str, pos: int) -> str:
        """Return progress string: already guessed prefix + underscores."""
        return target[:pos].upper() + "*" * (len(target) - pos)

    def init_letters_state(self, chat_id, word_id, target, letters):
        self._letters_set_state(chat_id, {
            "word_id": word_id,
            "target": target,
            "current_pos": 0,
            "wrong_attempts": 0,
            "letters": letters,
        })

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

        type_id = random.randint(1, 3)  # type - 1 - find translate to word, 2 - word by translate, 3 - word by letters

        if type_id in (1,2):
            words = await self.get_words_to_learn(chat_id)
            words_list = words["variants"]
            words_list.append(words["correct_word"])

            word = words["correct_word"].word if type_id == 1 else getattr(words["correct_word"],
                                                                           f"translation_{self.lang}")
            answer_id = words["correct_word"].word_id
            message_text = (f'{answer_text}\n\n'
                            f'<b>{word}</b>\n\n'
                            f'{self.i18n.get(f'message-text-{type_id}')}')
            random.shuffle(words_list)

            keyboard = Keyboards.guess_word_keyboard(self.i18n, words_list, type_id, answer_id, self.lang)

        else:
            words = await self.get_words_to_learn(chat_id,0)
            correct_word = words["correct_word"]
            message_text = (f'{answer_text}\n\n'
                            f'{self.i18n.get(f'message-text-{type_id}')} "{getattr(correct_word, f"translation_{self.lang}")}"')

            letters = self._shuffle_letters_with_positions(correct_word.word)
            target = correct_word.word.lower().strip()
            self.init_letters_state(chat_id, correct_word.word_id, target, letters)
            keyboard = Keyboards.letters_keyboard(self.i18n, correct_word.word_id, letters)

        return {
            "message_text": message_text,
            "keyboard": keyboard
        }

    async def process_word(self, button_word, statistics_service: StatisticsService):
        """Handle answer for modes 1 and 2 (multiple-choice by word/translation)."""
        correct_word = await self.get_word_by_id(button_word.correct_id)
        await statistics_service.save_statistic(button_word.chat_id,
                                                button_word.word_id,
                                                (1 if button_word.correct else 0),
                                                (0 if button_word.correct else 1)
                                                )

        return (f'{self.i18n.correct.answer() if button_word.correct else self.i18n.wrong.answer()}\n\n'
                f'{getattr(correct_word, f'translation_{self.lang}') if button_word.type_id == "1" else correct_word.word} '
                f'- {correct_word.word if button_word.type_id == "1" else getattr(correct_word, f'translation_{self.lang}')}\n\n'
                f'<code>{correct_word.example}\n'
                f'{getattr(correct_word, f'example_{self.lang}')}</code>')

    async def process_letters(self,
                              button_word,
                              statistics_service: StatisticsService) -> tuple[str, InlineKeyboardMarkup|None]:
        letter_attempts = self.default_settings.answer_set.letter_attempts
        chat_id = button_word.chat_id
        word_id = button_word.word_id
        index = button_word.index

        state = self._letters_get_state(chat_id)
        if not state or state["word_id"] != word_id:
            return self.i18n.error.no.current.word(), Keyboards.cancel_learning_keyboard(self.i18n)

        target = state["target"]
        letters = state["letters"]
        pos = state["current_pos"]
        wrong = state["wrong_attempts"]

        actual = target[index]
        expected = target[pos]

        # Correct
        if actual == expected:
            pos += 1
            state["current_pos"] = pos
            progress = self._build_progress(target, pos)

            if pos < len(target):
                text = self.i18n.correct.letter() + f'<b>{progress}</b>'
                kb = Keyboards.letters_keyboard(self.i18n, word_id, [l for l in letters if l[0] >= pos])
                self._letters_set_state(chat_id, state)
                return text, kb

            # Completed
            self._letters_clear_state(chat_id)
            await statistics_service.save_statistic(chat_id, word_id, correct=1, wrong=0)

            w = await self.get_word_by_id(word_id)
            text = f"{self.i18n.correct.word.by.letters()}: {target} ({getattr(w, f'translation_{self.lang}')})"
            button_word.correct = True
            kb = Keyboards.answer_word_keyboard(self.i18n, button_word)
            return text, kb

        # Wrong letter
        wrong += 1
        state["wrong_attempts"] = wrong

        progress = self._build_progress(target, pos)

        if wrong < letter_attempts:
            text = self.i18n.incorrect.letter() + f'<b>{progress}</b>'
            kb = Keyboards.letters_keyboard(self.i18n, word_id, [l for l in letters if l[0] >= pos])
            self._letters_set_state(chat_id, state)
            return text, kb

        # Fail (N mistakes)
        self._letters_clear_state(chat_id)
        await statistics_service.save_statistic(chat_id, word_id, correct=0, wrong=1)

        w = await self.get_word_by_id(word_id)
        text = f"{self.i18n.incorrect.word.by.letters()}: {target} ({getattr(w, f'translation_{self.lang}')})"
        button_word.correct = False
        kb = Keyboards.answer_word_keyboard(self.i18n, button_word)
        return text, kb
