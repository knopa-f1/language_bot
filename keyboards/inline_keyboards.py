from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder
from fluentogram import TranslatorRunner
from utils.i18n import Language


# Функция для формирования инлайн-клавиатуры на лету
def create_inline_kb(width: int,
                     i18n: TranslatorRunner,
                     *args: str,
                     last_btn: str | None = None,
                     **kwargs: str) -> InlineKeyboardMarkup:
    # Инициализируем билдер
    kb_builder = InlineKeyboardBuilder()
    # Инициализируем список для кнопок
    buttons: list[InlineKeyboardButton] = []

    # Заполняем список кнопками из аргументов args и kwargs
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

    # Распаковываем список с кнопками в билдер методом row c параметром width
    kb_builder.row(*buttons, width=width)
    # Добавляем в билдер последнюю кнопку, если она передана в функцию
    if last_btn:
        kb_builder.row(InlineKeyboardButton(
            text=i18n.get(last_btn),
            callback_data=last_btn
        ))

    # Возвращаем объект инлайн-клавиатуры
    return kb_builder.as_markup()

class Keyboards:
    @staticmethod
    def start_keyboard(i18n: TranslatorRunner):
        return create_inline_kb(2, i18n, 'button-start', 'button-settings')


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
    def guess_word_keyboard(i18n: TranslatorRunner, words_list: list[tuple], type_id: int, correct_id: int):
        # key = 'buttonWord_{word_id}_{answer_id}_{type}_{correct}'
        buttons = {f'button-word_{w_info[0]}_{correct_id}_{type_id}_{int(correct_id == w_info[0])}':
                       w_info[2 if type_id == 1 else 1] for w_info in words_list}
        return create_inline_kb(2, i18n, **buttons)

    @staticmethod
    def answer_word_keyboard(i18n: TranslatorRunner, word_info):
        buttons = {f'button-already-learned_{word_info.correct_id}_{word_info.type_id}':
                    i18n.get(f"button-already-learned-{int(word_info.correct)}"),
                   "button-start": i18n.button.next()}
        return create_inline_kb(2, i18n, last_btn="button-cancel-learning", **buttons)
