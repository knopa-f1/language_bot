import asyncio
import logging

from aiogram import Bot, Dispatcher
from config_data.constants import DefaultSettings
from database.database import Database

from keyboards.set_menu import set_main_menu
from config_data.config import Config, load_config
from handlers import other_handlers, user_handlers
from servises.schedule_tasks import job_send_messages_to_users

from apscheduler.schedulers.asyncio import AsyncIOScheduler

from fluentogram import TranslatorHub
from middlewares.i18n import TranslatorRunnerMiddleware
from servises.users_cache import UsersCache
from utils.i18n import create_translator_hub

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

# Инициализируем логгер модуля
logger = logging.getLogger(__name__)

# Функция конфигурирования и запуска бота
async def main():
    # Загружаем конфиг в переменную config
    config: Config = load_config()

    # Инициализируем бот и диспетчер
    bot = Bot(token=config.tg_bot.token)
    dp = Dispatcher()

    # Загружаем настройки по умолчанию
    dp["default_settings"] = DefaultSettings()
    # Загружаем бд
    bot_database = Database()
    dp["bot_database"] = bot_database
    # Загружаем кэш
    dp["users_cache"] = UsersCache()

    # Создаем объект типа TranslatorHub
    translator_hub: TranslatorHub = create_translator_hub()

    scheduler: AsyncIOScheduler = AsyncIOScheduler()

    # Настраиваем кнопку Menu
    await set_main_menu(bot)

    # Регистриуем роутеры в диспетчере
    dp.include_router(user_handlers.router)
    dp.include_router(other_handlers.router)

    # Запуск рассылки каждый час
    scheduler.add_job(job_send_messages_to_users, 'cron', hour='*', args=(bot, translator_hub, bot_database))
    #scheduler.add_job(job_send_messages_to_users, 'cron', minute='*', args=(bot,))
    scheduler.start()

    # Регистрируем миддлвар для i18n
    dp.update.middleware(TranslatorRunnerMiddleware())

    # Пропускаем накопившиеся апдейты и запускаем polling
    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot, allowed_updates=['message', 'callback_query'], _translator_hub=translator_hub)

asyncio.run(main())