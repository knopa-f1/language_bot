from aiogram import Router, F
from aiogram.filters import Command, CommandStart
from aiogram.types import Message
from lexicon.lexicon import LEXICON_RU, LEXICON_BUTTONS_RU
from aiogram.types import (KeyboardButton, Message, ReplyKeyboardMarkup,
                           ReplyKeyboardRemove, CallbackQuery)
from keyboards.inline_keyboards import (start_keyboard, settings_keyboard, time_keyboard, frequency_keyboard,
                                        answer_word_keyboard, learn_keyboard)
from database.database import bot_database
from servises.servises import get_selected_number, get_selected_end_time, prepare_words_to_learn, WordInfo

# Инициализируем роутер уровня модуля
router = Router()


# Этот хэндлер срабатывает на команду /start
@router.message(CommandStart())
async def process_start_command(message: Message):
    keyboard = start_keyboard()
    await message.answer(
        text=LEXICON_RU['/start'],
        reply_markup=(keyboard),

    )
    bot_database.users_settings.create(message.from_user.id)


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

# Этот хэндлер срабатывает на команду /settings
@router.message(Command(commands='statistics'))
async def process_settings_command(message: Message):
    keyboard = learn_keyboard()
    await message.answer(text=bot_database.words_interface.get_statistics(message.from_user.id),
                         reply_markup=keyboard)


# Этот хэндлер будет срабатывать на апдейт типа CallbackQuery
# с data 'buttonSettings'
@router.callback_query(F.data == 'buttonSettings')
async def process_button_settings_press(callback: CallbackQuery):
    keyboard = settings_keyboard()

    await callback.message.edit_text(
        text=bot_database.users_settings.get(callback.from_user.id),
        reply_markup=keyboard
    )


# Этот хэндлер будет срабатывать на апдейт типа CallbackQuery
# с data 'buttonCancelSettings'
@router.callback_query(F.data == 'buttonCancelSettings')
async def process_button_cancel_settings_press(callback: CallbackQuery):
    keyboard = learn_keyboard()

    await callback.message.edit_text(
        text=LEXICON_RU['cancel_settings'],
        reply_markup=keyboard
    )


# Этот хэндлер будет срабатывать на апдейт типа CallbackQuery
# с data 'buttonChangeTime'
@router.callback_query(F.data == 'buttonChangeTime')
async def process_button_change_time_press(callback: CallbackQuery):
    keyboard = time_keyboard()

    await callback.message.edit_text(
        text=LEXICON_RU['change_start_time'],
        reply_markup=keyboard
    )


# Этот хэндлер будет срабатывать на апдейт типа CallbackQuery
# с data 'buttonStartTime'
@router.callback_query(F.data.startswith('buttonStartTime'))
async def process_button_start_time_press(callback: CallbackQuery):
    selected_start_time = get_selected_number(callback.data)
    keyboard = time_keyboard(f"buttonEndTime_{selected_start_time}", selected_start_time)

    await callback.message.edit_text(
        text=LEXICON_RU['change_end_time'],
        reply_markup=keyboard
    )


# Этот хэндлер будет срабатывать на апдейт типа CallbackQuery
# с data 'buttonEndTime'
@router.callback_query(F.data.startswith('buttonEndTime'))
async def process_button_end_time_press(callback: CallbackQuery):
    selected_times = get_selected_end_time(callback.data)
    bot_database.users_settings.save(callback.from_user.id,
                                     start_time=selected_times[0],
                                     end_time=selected_times[1])

    keyboard = learn_keyboard()
    await callback.message.edit_text(text=LEXICON_RU['saved_settings'],
                                  reply_markup=keyboard)


# Этот хэндлер будет срабатывать на апдейт типа CallbackQuery
# с data 'buttonChangeFrequency'
@router.callback_query(F.data == 'buttonChangeFrequency')
async def process_button_change_frequency_press(callback: CallbackQuery):
    keyboard = frequency_keyboard()

    await callback.message.edit_text(
        text=LEXICON_RU['change_frequency'],
        reply_markup=keyboard
    )


# Этот хэндлер будет срабатывать на апдейт типа CallbackQuery
# с data 'buttonFrequency'
@router.callback_query(F.data.startswith('buttonFrequency'))
async def process_button_frequency_time_press(callback: CallbackQuery):
    bot_database.users_settings.save(callback.from_user.id,
                                     frequency=get_selected_number(callback.data, "button_frequency_"))

    keyboard = learn_keyboard()
    await callback.message.edit_text(text=LEXICON_RU['saved_settings'],
                                  reply_markup=keyboard)

# Этот хэндлер будет срабатывать на апдейт типа CallbackQuery
# с data 'button_start'
@router.callback_query(F.data == 'buttonStart')
async def process_button_start(callback: CallbackQuery, answer_text = ""):
    w_dict = prepare_words_to_learn(callback.from_user.id, answer_text)

    await callback.message.edit_text(
        text= w_dict["message_text"],
        reply_markup=w_dict["keyboard"]
    )

# Этот хэндлер будет срабатывать на апдейт типа CallbackQuery
# с data 'buttonWord_'
@router.callback_query(F.data.startswith('buttonWord_'))
async def process_button_word(callback: CallbackQuery):
    word_info = WordInfo(callback.from_user.id, callback.data)
    message_text = word_info.answer_message()
    keyboard = answer_word_keyboard(word_info)
    await callback.message.edit_text(
        message_text,
        reply_markup=keyboard
    )

# Этот хэндлер будет срабатывать на апдейт типа CallbackQuery
# с data 'buttonCancelLearning'
@router.callback_query(F.data.startswith('buttonCancelLearning'))
async def process_button_cancel_learning(callback: CallbackQuery):
    keyboard = learn_keyboard()
    await callback.message.edit_text(text=LEXICON_RU['cancel_learning'],
                                  reply_markup=keyboard)

# Этот хэндлер будет срабатывать на апдейт типа CallbackQuery
# с data 'buttonAlreadyLearned'
@router.callback_query(F.data.startswith('buttonAlreadyLearned'))
async def process_button_already_know_word(callback: CallbackQuery):
    WordInfo(callback.from_user.id, callback.data).mark_word_as_never_learn()
    await process_button_start(callback, LEXICON_RU['already_learned'])