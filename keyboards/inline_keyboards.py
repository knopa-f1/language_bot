import logging

from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder
from fluentogram import TranslatorRunner

from config_data.constants import DefaultSettings
from db.models import Word
from utils.i18n import Language

logger = logging.getLogger(__name__)


# creating keyboards
def create_inline_kb(
    width: int,
    i18n: TranslatorRunner,
    *args: str,
    last_btn: str | None = None,
    **kwargs: str,
) -> InlineKeyboardMarkup:
    kb_builder = InlineKeyboardBuilder()
    buttons: list[InlineKeyboardButton] = []

    if args:
        for button in args:
            buttons.append(InlineKeyboardButton(text=i18n.get(button), callback_data=button))
    if kwargs:
        for button, text in kwargs.items():
            buttons.append(InlineKeyboardButton(text=text, callback_data=button))

    kb_builder.row(*buttons, width=width)
    if last_btn:
        kb_builder.row(InlineKeyboardButton(text=i18n.get(last_btn), callback_data=last_btn))

    return kb_builder.as_markup()


class Keyboards:
    @staticmethod
    def start_keyboard(i18n: TranslatorRunner):
        return create_inline_kb(2, i18n, "button-settings", "button-statistics", "button-start")

    @staticmethod
    def learn_keyboard(i18n: TranslatorRunner):
        return create_inline_kb(2, i18n, "button-settings", "button-statistics", "button-start")

    @staticmethod
    def reminder_keyboard(i18n: TranslatorRunner):
        return create_inline_kb(1, i18n, "button-reminder")

    @staticmethod
    def stat_keyboard(i18n: TranslatorRunner):
        return create_inline_kb(2, i18n, "button-settings", "button-start")

    def cancel_learning_keyboard(i18n: TranslatorRunner):
        return create_inline_kb(2, i18n, "button-cancel-learning")

    @staticmethod
    def settings_keyboard(i18n: TranslatorRunner):
        return create_inline_kb(
            1,
            i18n,
            "button-change-time",
            "button-change-frequency",
            "button-change-word-count",
            "button-change-language",
            last_btn="button-cancel-settings",
        )

    @staticmethod
    def time_keyboard(
        i18n: TranslatorRunner,
        pref: str = "button-start-time",
        start: int = 0,
        end: int = 23,
    ):
        buttons = {f"{pref}_{i}": str(i) for i in range(start, end + 1)}
        return create_inline_kb(8, i18n, last_btn="button-cancel-settings", **buttons)

    @staticmethod
    def frequency_keyboard(i18n: TranslatorRunner, start: int = 0, end: int = 24):
        buttons = {f"button-frequency_{i}": str(i) for i in range(start, end + 1)}
        return create_inline_kb(8, i18n, last_btn="button-cancel-settings", **buttons)

    @staticmethod
    def language_keyboard(i18n: TranslatorRunner):
        buttons = {f"button-language_{lan.name}": lan.value for lan in Language}
        return create_inline_kb(3, i18n, last_btn="button-cancel-settings", **buttons)

    @staticmethod
    def language_start_keyboard(i18n: TranslatorRunner):
        buttons = {f"button-language-start_{lan.name}": lan.value for lan in Language}
        return create_inline_kb(3, i18n, **buttons)

    @staticmethod
    def word_count_keyboard(i18n: TranslatorRunner, default_settings: DefaultSettings | None):
        if default_settings is None:
            buttons = {}
        else:
            buttons = {
                f"button-word-count_{number}": str(number) for number in default_settings.answer_set.vars_count_current
            }
        return create_inline_kb(3, i18n, last_btn="button-cancel-settings", **buttons)

    @staticmethod
    def guess_word_keyboard(
        i18n: TranslatorRunner,
        words_list: list[Word],
        type_id: int,
        correct_id: int,
        lang,
    ):
        # key = 'button-word_{word_id}_{answer_id}_{type}_{correct}'
        buttons = {
            f"button-word_{word.word_id}_{correct_id}_{type_id}_{int(correct_id == word.word_id)}": getattr(
                word, f"translation_{lang}" if type_id == 1 else "word"
            )
            for word in words_list
        }
        return create_inline_kb(1, i18n, **buttons)

    @staticmethod
    def letters_keyboard(i18n: TranslatorRunner, word_id: Word, shuffled_letters: list):
        # key = 'button-letter_{word_id}_{letter_id}'
        buttons = {f"button-letter_{word_id}_{index}": letter for index, letter in shuffled_letters}
        return create_inline_kb(
            min(len(shuffled_letters), 8),
            i18n,
            last_btn="button-cancel-learning",
            **buttons,
        )

    @staticmethod
    def answer_word_keyboard(i18n: TranslatorRunner, word_info):
        buttons = {
            "button-cancel-learning": i18n.button.cancel.learning(),
            f"button-already-learned_{word_info.correct_id}_{word_info.type_id}": i18n.get(
                f"button-already-learned-{int(word_info.correct)}"
            ),
            "button-next": i18n.button.next(),
        }
        return create_inline_kb(2, i18n, **buttons)
