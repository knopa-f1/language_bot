import logging

from aiogram import Router, F
from aiogram.filters import Command, CommandStart
from aiogram.types import (Message, CallbackQuery)
from keyboards.inline_keyboards import Keyboards
from servises.buttons_services import get_selected_data, get_selected_end_time, ButtonWord
from servises.users_service import UsersService

logger = logging.getLogger(__name__)

# router initialization
router = Router()


# command /start
@router.message(CommandStart())
async def process_start_command(message: Message,
                                user_service: UsersService):
    if await user_service.user_settings_exists(message.from_user.id):
        # user is already in settings, should not ask a lang
        keyboard = Keyboards.start_keyboard(user_service.i18n)
        text = user_service.i18n.start()
    else:
        # ask a lang
        keyboard = Keyboards.language_start_keyboard(user_service.i18n)
        text = user_service.i18n.change.language()

    await message.answer(
        text=text,
        reply_markup=keyboard
    )


# command /help
@router.message(Command(commands='help'))
async def process_help_command(message: Message, user_service: UsersService):
    await message.answer(text=user_service.i18n.help())


# command /settings
@router.message(Command(commands='settings'))
async def process_settings_command(message: Message, user_service: UsersService):
    keyboard = Keyboards.settings_keyboard(user_service.i18n)
    await message.answer(text=await user_service.get_user_settings_description(message.from_user.id),
                         reply_markup=keyboard)


# command /statistics
@router.message(Command(commands='statistics'))
async def process_settings_command(message: Message, user_service: UsersService):
    keyboard = Keyboards.learn_keyboard(user_service.i18n)
    await message.answer(text=await user_service.get_statistics_description(message.from_user.id),
                         reply_markup=keyboard)


# CallbackQuery data 'button-settings'
@router.callback_query(F.data == 'button-settings')
async def process_button_settings_press(callback: CallbackQuery, user_service: UsersService):
    keyboard = Keyboards.settings_keyboard(user_service.i18n)

    await callback.message.edit_text(
        text=await user_service.get_user_settings_description(callback.from_user.id),
        reply_markup=keyboard
    )


# CallbackQuery data 'button-cancel-settings'
@router.callback_query(F.data == 'button-cancel-settings')
async def process_button_cancel_settings_press(callback: CallbackQuery, user_service: UsersService):
    keyboard = Keyboards.learn_keyboard(user_service.i18n)

    await callback.message.edit_text(
        text=user_service.i18n.cancel.settings(),
        reply_markup=keyboard
    )


# CallbackQuery data 'button-change-time'
@router.callback_query(F.data == 'button-change-time')
async def process_button_change_time_press(callback: CallbackQuery, user_service: UsersService):
    keyboard = Keyboards.time_keyboard(user_service.i18n)

    await callback.message.edit_text(
        text=user_service.i18n.change.start.time(),
        reply_markup=keyboard
    )


# CallbackQuery data 'button-start-time'
@router.callback_query(F.data.startswith('button-start-time'))
async def process_button_start_time_press(callback: CallbackQuery, user_service: UsersService):
    selected_start_time = int(get_selected_data(callback.data))
    keyboard = Keyboards.time_keyboard(user_service.i18n, f"button-end-time_{selected_start_time}", selected_start_time)

    await callback.message.edit_text(
        text=user_service.i18n.change.end.time(),
        reply_markup=keyboard
    )


# CallbackQuery data 'button-end-time'
@router.callback_query(F.data.startswith('button-end-time'))
async def process_button_end_time_press(callback: CallbackQuery, user_service: UsersService):
    selected_times = get_selected_end_time(callback.data)
    await user_service.set_user_settings(callback.from_user.id,
                                         start_time=selected_times[0],
                                         end_time=selected_times[1])

    keyboard = Keyboards.learn_keyboard(user_service.i18n)
    await callback.message.edit_text(text=user_service.i18n.saved.settings(),
                                     reply_markup=keyboard)


# CallbackQuery data 'button-change-frequency'
@router.callback_query(F.data == 'button-change-frequency')
async def process_button_change_frequency_press(callback: CallbackQuery, user_service: UsersService):
    keyboard = Keyboards.frequency_keyboard(user_service.i18n)

    await callback.message.edit_text(
        text=user_service.i18n.change.frequency(),
        reply_markup=keyboard
    )


# CallbackQuery data 'button-frequency'
@router.callback_query(F.data.startswith('button-frequency'))
async def process_button_frequency_press(callback: CallbackQuery, user_service: UsersService):
    await user_service.set_user_settings(callback.from_user.id,
                                         frequency=int(get_selected_data(callback.data)))

    keyboard = Keyboards.learn_keyboard(user_service.i18n)
    await callback.message.edit_text(text=user_service.i18n.saved.settings(),
                                     reply_markup=keyboard)


# CallbackQuery data 'button-change-language'
@router.callback_query(F.data == 'button-change-language')
async def process_button_change_language_press(callback: CallbackQuery, user_service: UsersService):
    keyboard = Keyboards.language_keyboard(user_service.i18n)

    await callback.message.edit_text(
        text=user_service.i18n.change.language(),
        reply_markup=keyboard
    )


# CallbackQuery data 'button-language'
@router.callback_query(F.data.startswith('button-language'))
async def process_button_language_press(callback: CallbackQuery,
                                        user_service: UsersService):
    await user_service.set_user_settings(callback.from_user.id, lang=user_service.lang)
    if callback.data.startswith("button-language-start"):
        keyboard = Keyboards.start_keyboard(user_service.i18n)
        text = user_service.i18n.start()
    else:
        keyboard = Keyboards.learn_keyboard(user_service.i18n)
        text = user_service.i18n.saved.settings()

    await callback.message.edit_text(text=text,
                                     reply_markup=keyboard)


# CallbackQuery data 'button-start'
@router.callback_query(F.data.in_({'button-next', 'button-start'}))
async def process_button_start(callback: CallbackQuery,
                               user_service: UsersService,
                               answer_text: str = ""):
    w_dict = await user_service.prepare_words_to_learn(callback.from_user.id, answer_text)

    await callback.message.edit_text(
        text=w_dict["message_text"],
        reply_markup=w_dict["keyboard"]
    )


# CallbackQuery data 'button-word'
@router.callback_query(F.data.startswith('button-word'))
async def process_button_word(callback: CallbackQuery, user_service: UsersService):
    button_word = ButtonWord(callback.from_user.id, callback.data)
    message_text = await button_word.answer_message(user_service)
    keyboard = Keyboards.answer_word_keyboard(user_service.i18n, button_word)
    await callback.message.edit_text(
        message_text,
        reply_markup=keyboard
    )


# CallbackQuery data 'button-cancel-learning'
@router.callback_query(F.data.startswith('button-cancel-learning'))
async def process_button_cancel_learning(callback: CallbackQuery, user_service: UsersService):
    keyboard = Keyboards.learn_keyboard(user_service.i18n)
    await callback.message.edit_text(text=user_service.i18n.cancel.learning(),
                                     reply_markup=keyboard)


# CallbackQuery data 'button-already-learned'
@router.callback_query(F.data.startswith('button-already-learned'))
async def process_button_already_know_word(callback: CallbackQuery, user_service: UsersService):
    await ButtonWord(callback.from_user.id, callback.data).mark_word_as_never_learn(user_service)
    await process_button_start(callback, user_service, user_service.i18n.already.learned())
