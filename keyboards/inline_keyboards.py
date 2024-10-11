from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder
from lexicon.lexicon import LEXICON_BUTTONS_RU


# Функция для формирования инлайн-клавиатуры на лету
def create_inline_kb(width: int,
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
                text=LEXICON_BUTTONS_RU[button] if button in LEXICON_BUTTONS_RU else button,
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
            text=LEXICON_BUTTONS_RU[last_btn] if last_btn in LEXICON_BUTTONS_RU else last_btn,
            callback_data=last_btn
        ))

    # Возвращаем объект инлайн-клавиатуры
    return kb_builder.as_markup()

def start_keyboard():
    return create_inline_kb(2, 'buttonStart', 'buttonSettings')

def learn_keyboard():
    return create_inline_kb(2, 'buttonStart')

def settings_keyboard():
    return create_inline_kb(3, 'buttonChangeTime', 'buttonChangeFrequency', last_btn="buttonCancelSettings")

def time_keyboard(pref: str = "buttonStartTime", start: int = 0, end: int = 23):
    buttons = {f'{pref}_{i}': str(i) for i in range(start, end + 1)}
    return create_inline_kb(8, last_btn="buttonCancelSettings", **buttons)

def frequency_keyboard(start: int = 1, end: int = 24):
    buttons = {f'buttonFrequency_{i}': str(i) for i in range(start, end + 1)}
    return create_inline_kb(8, last_btn="buttonCancelSettings", **buttons)

def guess_word_keyboard(words_list: list[tuple], type_id:int, correct_id:int):
    # key = 'buttonWord_{word_id}_{answer_id}_{type}_{correct}'
    buttons = {f'buttonWord_{w_info[0]}_{correct_id}_{type_id}_{int(correct_id == w_info[0])}':
                   w_info[2 if type_id == 1 else 1] for w_info in words_list}
    return create_inline_kb(2,  **buttons)

def answer_word_keyboard(word_info):
    buttons = {f'buttonAlreadyLearned_{word_info.correct_id}_{word_info.type_id}':
                   LEXICON_BUTTONS_RU[f"buttonAlreadyLearned_{int(word_info.correct)}"],
               "buttonStart":  LEXICON_BUTTONS_RU["buttonContinue"],}
    return create_inline_kb(2, last_btn="buttonCancelLearning", **buttons)


