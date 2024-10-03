from aiogram import Router, F
from aiogram.filters import Command, CommandStart
from aiogram.types import Message
from lexicon.lexicon import LEXICON_RU, LEXICON_BUTTONS_RU
from aiogram.types import (KeyboardButton, Message, ReplyKeyboardMarkup,
                           ReplyKeyboardRemove, CallbackQuery)
from keyboards.inline_keyboards import start_keyboard, settings_keyboard, time_keyboard, frequency_keyboard
from database.database import bot_database
from servises.servises import get_selected_number

# Инициализируем роутер уровня модуля
router = Router()


# Этот хэндлер срабатывает на команду /start
@router.message(CommandStart())
async def process_start_command(message: Message):
    keyboard = start_keyboard()
    await message.answer(
        text=LEXICON_RU['/start'],
        reply_markup=keyboard
    )
    bot_database.users_settings.create(message.from_user.id)
    bot_database.users_cache.create(message.from_user.id)


# Этот хэндлер срабатывает на команду /help
@router.message(Command(commands='help'))
async def process_help_command(message: Message):
    await message.answer(text=LEXICON_RU['/help'])


# Этот хэндлер срабатывает на команду /settings
@router.message(Command(commands='settings'))
async def process_settings_command(message: Message):
    keyboard = settings_keyboard()
    await message.answer(text=bot_database.users_settings.get(message.from_user.id),
                         reply_markup=keyboard)


# Этот хэндлер будет срабатывать на апдейт типа CallbackQuery
# с data 'button_settings'
@router.callback_query(F.data == 'button_settings')
async def process_button_settings_press(callback: CallbackQuery):
    keyboard = settings_keyboard()

    await callback.answer()
    await callback.message.answer(
        text=bot_database.users_settings.get(callback.from_user.id),
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
    bot_database.users_cache.add(callback.from_user.id, "start_time", selected_start_time)

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
    bot_database.users_settings.save(callback.from_user.id,
                                     start_time=bot_database.users_cache.get(callback.from_user.id, "start_time"),
                                     end_time=get_selected_number(callback.data, "button_end_time_"))

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
async def process_button_frequency_time_press(callback: CallbackQuery):
    bot_database.users_settings.save(callback.from_user.id,
                                     frequency=get_selected_number(callback.data, "button_frequency_"))

    keyboard = start_keyboard()
    await callback.answer()
    await callback.message.answer(text=LEXICON_RU['saved_settings'],
                                  reply_markup=keyboard)
