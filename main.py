import asyncio
import logging

from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties

from keyboards.set_menu import set_main_menu
from config_data.config import Config, load_config
from handlers import other_handlers, user_handlers
from servises.schedule_tasks import job_send_messages_to_users

from apscheduler.schedulers.asyncio import AsyncIOScheduler

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

# Функция конфигурирования и запуска бота
async def main():
    # Загружаем конфиг в переменную config
    config: Config = load_config()

    # Инициализируем бот и диспетчер
    bot = Bot(token=config.tg_bot.token)
    dp = Dispatcher()

    scheduler: AsyncIOScheduler = AsyncIOScheduler()

    # Настраиваем кнопку Menu
    await set_main_menu(bot)

    # Регистриуем роутеры в диспетчере
    dp.include_router(user_handlers.router)
    dp.include_router(other_handlers.router)

    # Запуск рассылки каждый час
    #scheduler.add_job(job_send_messages_to_users, 'cron', hour='*', args=(bot,))
    scheduler.add_job(job_send_messages_to_users, 'cron', minute='*', args=(bot,))
    scheduler.start()

    # Пропускаем накопившиеся апдейты и запускаем polling
    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot, allowed_updates=['message', 'callback_query'])

asyncio.run(main())