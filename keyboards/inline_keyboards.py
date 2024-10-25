from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder
from db.models import Word
from fluentogram import TranslatorRunner
from utils.i18n import Language
import logging

logger = logging.getLogger(__name__)


# creating keyboards
def create_inline_kb(width: int,
                     i18n: TranslatorRunner,
                     *args: str,
                     last_btn: str | None = None,
                     **kwargs: str) -> InlineKeyboardMarkup:
    kb_builder = InlineKeyboardBuilder()
    buttons: list[InlineKeyboardButton] = []

    if args:
        for button in args:
            buttons.append(InlineKeyboardButton(
                text=i18n.get(button),
                callback_data=button
            ))
    if kwargs:
        for button, text in kwargs.items():
            buttons.append(InlineKeyboardButton(
                text=text,
                callback_data=button))

    kb_builder.row(*buttons, width=width)
    if last_btn:
        kb_builder.row(InlineKeyboardButton(
            text=i18n.get(last_btn),
            callback_data=last_btn
        ))

    return kb_builder.as_markup()


class Keyboards:
    @staticmethod
    def start_keyboard(i18n: TranslatorRunner):
        return create_inline_kb(2, i18n, 'button-settings', 'button-start')

    @staticmethod
    def learn_keyboard(i18n: TranslatorRunner):
        return create_inline_kb(2, i18n, 'button-start')

    @staticmethod
    def settings_keyboard(i18n: TranslatorRunner):
        return create_inline_kb(3, i18n,
                                'button-change-time',
                                'button-change-frequency',
                                'button-change-language',
                                last_btn="button-cancel-settings")

    @staticmethod
    def time_keyboard(i18n: TranslatorRunner, pref: str = "button-start-time", start: int = 0, end: int = 23):
        buttons = {f'{pref}_{i}': str(i) for i in range(start, end + 1)}
        return create_inline_kb(8, i18n, last_btn="button-cancel-settings", **buttons)

    @staticmethod
    def frequency_keyboard(i18n: TranslatorRunner, start: int = 1, end: int = 24):
        buttons = {f'button-frequency_{i}': str(i) for i in range(start, end + 1)}
        return create_inline_kb(8, i18n, last_btn="button-cancel-settings", **buttons)

    @staticmethod
    def language_keyboard(i18n: TranslatorRunner):
        buttons = {f'button-language_{l.name}': l.value for l in Language}
        return create_inline_kb(3, i18n, last_btn="button-cancel-settings", **buttons)

    @staticmethod
    def language_start_keyboard(i18n: TranslatorRunner):
        buttons = {f'button-language-start_{l.name}': l.value for l in Language}
        return create_inline_kb(3, i18n, **buttons)

    @staticmethod
    def guess_word_keyboard(i18n: TranslatorRunner, words_list: list[Word], type_id: int, correct_id: int, lang):
        # key = 'buttonWord_{word_id}_{answer_id}_{type}_{correct}'
        buttons = {f'button-word_{word.word_id}_{correct_id}_{type_id}_{int(correct_id == word.word_id)}':
                       getattr(word, f'translation_{lang}' if type_id == 1 else "word") for word in words_list}
        return create_inline_kb(1, i18n, **buttons)

    @staticmethod
    def answer_word_keyboard(i18n: TranslatorRunner, word_info):
        buttons = {"button-cancel-learning": i18n.button.cancel.learning(),
                   f'button-already-learned_{word_info.correct_id}_{word_info.type_id}':
                       i18n.get(f"button-already-learned-{int(word_info.correct)}"),
                   "button-next": i18n.button.next()}
        return create_inline_kb(2, i18n, **buttons)
