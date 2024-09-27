from copy import deepcopy

from aiogram import Router, F
from aiogram.filters import Command, CommandStart
from aiogram.types import Message
from lexicon.lexicon import LEXICON_RU, LEXICON_BUTTONS_RU
from aiogram.types import (KeyboardButton, Message, ReplyKeyboardMarkup,
                           ReplyKeyboardRemove, CallbackQuery)
from keyboards.inline_keyboards import start_keyboard, settings_keyboard, time_keyboard, frequency_keyboard
from database.database import users_settings_dict_template, load_users_words, load_users_settings, \
    save_users_settings, users_cache
from servises.servises import get_user_settings, save_user_settings, get_selected_number
# Инициализируем роутер уровня модуля
router = Router()

# Этот хэндлер срабатывает на команду /start
@router.message(CommandStart())
async def process_start_command(message: Message):
    users_settings = load_users_settings()
    keyboard = start_keyboard()
    user_id = str(message.from_user.id)
    await message.answer(
        text=LEXICON_RU['/start'],
        reply_markup=keyboard
    )

    if user_id not in users_settings:
        users_settings.setdefault(user_id, deepcopy(users_settings_dict_template))
        users_cache.setdefault(user_id, deepcopy(users_settings_dict_template))
        save_users_settings(users_settings)


# Этот хэндлер срабатывает на команду /help
@router.message(Command(commands='help'))
async def process_help_command(message: Message):
    await message.answer(text=LEXICON_RU['/help'])

# Этот хэндлер срабатывает на команду /settings
@router.message(Command(commands='settings'))
async def process_settings_command(message: Message):
    keyboard = settings_keyboard()
    await message.answer(text=get_user_settings(str(message.from_user.id)),
                         reply_markup=keyboard)


# Этот хэндлер будет срабатывать на апдейт типа CallbackQuery
# с data 'button_settings'
@router.callback_query(F.data == 'button_settings')
async def process_button_settings_press(callback: CallbackQuery):
    keyboard = settings_keyboard()

    await callback.answer()
    await callback.message.answer(
        text=get_user_settings(str(callback.from_user.id)),
        reply_markup=keyboard
    )

# Этот хэндлер будет срабатывать на апдейт типа CallbackQuery
# с data 'button_cancel_settings'
@router.callback_query(F.data == 'button_cancel_settings')
async def process_button_settings_press(callback: CallbackQuery):
    keyboard = start_keyboard()

    await callback.answer()
    await callback.message.answer(
        text=LEXICON_RU['cancel_settings'],
        reply_markup=keyboard
    )

# Этот хэндлер будет срабатывать на апдейт типа CallbackQuery
# с data 'button_change_time'
@router.callback_query(F.data == 'button_change_time')
async def process_button_change_time_press(callback: CallbackQuery):
    keyboard = time_keyboard()

    await callback.answer()
    await callback.message.answer(
        text=LEXICON_RU['change_start_time'],
        reply_markup=keyboard
    )

# Этот хэндлер будет срабатывать на апдейт типа CallbackQuery
# с data 'button_start_time'
@router.callback_query(F.data.startswith('button_start_time'))
async def process_button_start_time_press(callback: CallbackQuery):
    selected_start_time = get_selected_number(callback.data)
    user_id = str(callback.from_user.id)
    if user_id not in users_cache:
        users_cache[user_id] = {}
    users_cache[user_id]["start_time"] = selected_start_time
    keyboard = time_keyboard("button_end_time", selected_start_time)

    await callback.answer()
    await callback.message.answer(
        text=LEXICON_RU['change_end_time'],
        reply_markup=keyboard
    )

# Этот хэндлер будет срабатывать на апдейт типа CallbackQuery
# с data 'button_end_time'
@router.callback_query(F.data.startswith('button_end_time'))
async def process_button_end_time_press(callback: CallbackQuery):
    user_id = str(callback.from_user.id)
    save_user_settings(user_id, start_time = users_cache[user_id]["start_time"],
                       end_time = get_selected_number(callback.data, "button_end_time_"))

    keyboard = start_keyboard()
    await callback.answer()
    await callback.message.answer(text=LEXICON_RU['saved_settings'],
                                  reply_markup=keyboard)

# Этот хэндлер будет срабатывать на апдейт типа CallbackQuery
# с data 'button_change_frequency'
@router.callback_query(F.data == 'button_change_frequency')
async def process_button_change_frequency_press(callback: CallbackQuery):
    keyboard = frequency_keyboard()

    await callback.answer()
    await callback.message.answer(
        text=LEXICON_RU['change_frequency'],
        reply_markup=keyboard
    )

# Этот хэндлер будет срабатывать на апдейт типа CallbackQuery
# с data 'button_frequency'
@router.callback_query(F.data.startswith('button_frequency'))
async def process_button_end_time_press(callback: CallbackQuery):
    user_id = str(callback.from_user.id)
    save_user_settings(user_id, frequency=get_selected_number(callback.data, "button_frequency_"))

    keyboard = start_keyboard()
    await callback.answer()
    await callback.message.answer(text=LEXICON_RU['saved_settings'],
                                  reply_markup=keyboard)
