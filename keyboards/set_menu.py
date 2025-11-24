import logging

from aiogram import Bot
from fluentogram import TranslatorRunner

logger = logging.getLogger(__name__)


commands: dict[str, str] = {
    "/start": "command-start",
    "/help": "command-help",
    "/settings": "command-settings",
    "/statistics": "command-statistics",
}


async def set_main_menu(bot: Bot, i18n: TranslatorRunner):
    # main_menu_commands = [
    #     BotCommand(
    #         command=command,
    #         description=i18n.get(description)
    #     )
    #     for command, description in commands.items()
    # ]
    #
    # await bot.set_my_commands(main_menu_commands)
    await bot.set_my_commands([])
