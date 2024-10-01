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
    return create_inline_kb(2, 'button_start', 'button_settings')

def settings_keyboard():
    return create_inline_kb(3, 'button_change_time', 'button_change_frequency')

def time_keyboard(pref:str = "button_start_time", start: int = 0, end: int = 23):
    buttons = {f'{pref}_{i}': str(i) for i in range(start, end + 1)}
    return create_inline_kb(8, last_btn= "button_cancel_settings", **buttons)

def frequency_keyboard(start: int = 1, end: int = 24):
    buttons = {f'button_frequency_{i}': str(i) for i in range(start, end + 1)}
    return create_inline_kb(8, last_btn= "button_cancel_settings", **buttons)