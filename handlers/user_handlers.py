from aiogram import Router, F
from aiogram.filters import Command, CommandStart
from aiogram.types import (Message, CallbackQuery)
from config_data.constants import DefaultSettings
from keyboards.inline_keyboards import Keyboards
from database.database import Database
from servises.servises import get_selected_data, get_selected_end_time, prepare_words_to_learn, WordInfo
from fluentogram import TranslatorRunner
from servises.user_settings import UserSettings
from servises.users_cache import UsersCache

# Инициализируем роутер уровня модуля
router = Router()


# Этот хэндлер срабатывает на команду /start
@router.message(CommandStart())
async def process_start_command(message: Message,
                                i18n: TranslatorRunner,
                                bot_database: Database,
                                default_settings: DefaultSettings):
    bot_database.users_settings.create(message.from_user.id, default_settings, message.from_user.language_code)
    # user_lang = bot_database.get_user_lang(message.from_user.id)
    keyboard = Keyboards.start_keyboard(i18n)
    await message.answer(
        text=i18n.start(),
        reply_markup=keyboard,

    )


# Этот хэндлер срабатывает на команду /help
@router.message(Command(commands='help'))
async def process_help_command(message: Message, i18n: TranslatorRunner):
    await message.answer(text=i18n.help())


# Этот хэндлер срабатывает на команду /settings
@router.message(Command(commands='settings'))
async def process_settings_command(message: Message, i18n: TranslatorRunner, bot_database: Database):
    keyboard = Keyboards.settings_keyboard(i18n)
    await message.answer(text=bot_database.users_settings.get_description(message.from_user.id, i18n),
                         reply_markup=keyboard)


# Этот хэндлер срабатывает на команду /settings
@router.message(Command(commands='statistics'))
async def process_settings_command(message: Message, i18n: TranslatorRunner, bot_database: Database):
    keyboard = Keyboards.learn_keyboard(i18n)
    await message.answer(text=bot_database.words_interface.get_statistics(message.from_user.id, i18n),
                         reply_markup=keyboard)


# Этот хэндлер будет срабатывать на апдейт типа CallbackQuery
# с data 'button-settings'
@router.callback_query(F.data == 'button-settings')
async def process_button_settings_press(callback: CallbackQuery, i18n: TranslatorRunner, bot_database: Database):
    keyboard = Keyboards.settings_keyboard(i18n)

    await callback.message.edit_text(
        text=bot_database.users_settings.get_description(callback.from_user.id, i18n),
        reply_markup=keyboard
    )


# Этот хэндлер будет срабатывать на апдейт типа CallbackQuery
# с data 'button-cancel-settings'
@router.callback_query(F.data == 'button-cancel-settings')
async def process_button_cancel_settings_press(callback: CallbackQuery, i18n: TranslatorRunner):
    keyboard = Keyboards.learn_keyboard(i18n)

    await callback.message.edit_text(
        text=i18n.cancel.settings(),
        reply_markup=keyboard
    )


# Этот хэндлер будет срабатывать на апдейт типа CallbackQuery
# с data 'button-change-time'
@router.callback_query(F.data == 'button-change-time')
async def process_button_change_time_press(callback: CallbackQuery, i18n: TranslatorRunner):
    keyboard = Keyboards.time_keyboard(i18n)

    await callback.message.edit_text(
        text=i18n.change.start.time(),
        reply_markup=keyboard
    )


# Этот хэндлер будет срабатывать на апдейт типа CallbackQuery
# с data 'button-start-time'
@router.callback_query(F.data.startswith('button-start-time'))
async def process_button_start_time_press(callback: CallbackQuery, i18n: TranslatorRunner):
    selected_start_time = int(get_selected_data(callback.data))
    keyboard = Keyboards.time_keyboard(f"button-end-time_{selected_start_time}", selected_start_time)

    await callback.message.edit_text(
        text=i18n.change.end.time(),
        reply_markup=keyboard
    )


# Этот хэндлер будет срабатывать на апдейт типа CallbackQuery
# с data 'button-end-time'
@router.callback_query(F.data.startswith('button-end-time'))
async def process_button_end_time_press(callback: CallbackQuery, i18n: TranslatorRunner, bot_database: Database,
                                        default_settings: DefaultSettings):
    selected_times = get_selected_end_time(callback.data)
    bot_database.users_settings.set(callback.from_user.id,
                                    default_settings,
                                    start_time=selected_times[0],
                                    end_time=selected_times[1])

    keyboard = Keyboards.learn_keyboard(i18n)
    await callback.message.edit_text(text=i18n.saved.settings(),
                                     reply_markup=keyboard)


# Этот хэндлер будет срабатывать на апдейт типа CallbackQuery
# с data 'button-change-frequency'
@router.callback_query(F.data == 'button-change-frequency')
async def process_button_change_frequency_press(callback: CallbackQuery, i18n: TranslatorRunner):
    keyboard = Keyboards.frequency_keyboard(i18n)

    await callback.message.edit_text(
        text=i18n.change.frequency(),
        reply_markup=keyboard
    )


# Этот хэндлер будет срабатывать на апдейт типа CallbackQuery
# с data 'button-frequency'
@router.callback_query(F.data.startswith('button-frequency'))
async def process_button_frequency_press(callback: CallbackQuery, i18n: TranslatorRunner, bot_database: Database,
                                         default_settings:DefaultSettings):
    bot_database.users_settings.set(callback.from_user.id,
                                    default_settings,
                                    frequency=int(get_selected_data(callback.data, "button-frequency_")))

    keyboard = Keyboards.learn_keyboard(i18n)
    await callback.message.edit_text(text=i18n.saved.settings(),
                                     reply_markup=keyboard)


# Этот хэндлер будет срабатывать на апдейт типа CallbackQuery
# с data 'button-change-language'
@router.callback_query(F.data == 'button-change-language')
async def process_button_change_language_press(callback: CallbackQuery, i18n: TranslatorRunner):
    keyboard = Keyboards.language_keyboard(i18n)

    await callback.message.edit_text(
        text=i18n.change.language(),
        reply_markup=keyboard
    )


# Этот хэндлер будет срабатывать на апдейт типа CallbackQuery
# с data 'button-language'
@router.callback_query(F.data.startswith('button-language'))
async def process_button_language_press(callback: CallbackQuery,
                                        i18n: TranslatorRunner,
                                        bot_database: Database,
                                        users_cache: UsersCache,
                                        lang: str,
                                        default_settings: DefaultSettings):
    UserSettings.set(callback.from_user.id, bot_database, users_cache, default_settings, lang=lang)
    keyboard = Keyboards.learn_keyboard(i18n)
    await callback.message.edit_text(text=i18n.saved.settings(),
                                     reply_markup=keyboard)


# Этот хэндлер будет срабатывать на апдейт типа CallbackQuery
# с data 'button-start'
@router.callback_query(F.data == 'button-start')
async def process_button_start(callback: CallbackQuery,
                               i18n: TranslatorRunner,
                               bot_database: Database,
                               lang:str,
                               default_settings: DefaultSettings,
                               answer_text: str = ""):
    w_dict = prepare_words_to_learn(callback.from_user.id, i18n, lang, bot_database, default_settings, answer_text)

    await callback.message.edit_text(
        text=w_dict["message_text"],
        reply_markup=w_dict["keyboard"]
    )


# Этот хэндлер будет срабатывать на апдейт типа CallbackQuery
# с data 'button-word'
@router.callback_query(F.data.startswith('button-word'))
async def process_button_word(callback: CallbackQuery,
                              i18n: TranslatorRunner,
                              bot_database: Database,
                              lang: str,
                              default_settings: DefaultSettings):
    word_info = WordInfo(callback.from_user.id, callback.data)
    message_text = word_info.answer_message(i18n, lang,bot_database, default_settings)
    keyboard = Keyboards.answer_word_keyboard(i18n, word_info)
    await callback.message.edit_text(
        message_text,
        reply_markup=keyboard
    )


# Этот хэндлер будет срабатывать на апдейт типа CallbackQuery
# с data 'button-cancel-learning'
@router.callback_query(F.data.startswith('button-cancel-learning'))
async def process_button_cancel_learning(callback: CallbackQuery, i18n: TranslatorRunner):
    keyboard = Keyboards.learn_keyboard(i18n)
    await callback.message.edit_text(text=i18n.cancel.learning(),
                                     reply_markup=keyboard)


# Этот хэндлер будет срабатывать на апдейт типа CallbackQuery
# с data 'button-already-learned'
@router.callback_query(F.data.startswith('button-already-learned'))
async def process_button_already_know_word(callback: CallbackQuery,
                                           i18n: TranslatorRunner,
                                           bot_database: Database,
                                           lang: str,
                                           default_settings: DefaultSettings):
    WordInfo(callback.from_user.id, callback.data).mark_word_as_never_learn(bot_database, default_settings)
    await process_button_start(callback, i18n, bot_database, lang, default_settings, i18n.already.learned())
