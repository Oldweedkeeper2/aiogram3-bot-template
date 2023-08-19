import logging

from aiogram import Bot

from data.config import admins


async def on_startup_notify(bot: Bot):
    for admin in admins:
        try:
            bot_properties = await bot.me()
            await bot.send_message(admin, f"Бот запущен:\n\n"
                                          f"<b>Bot id:</> {bot_properties.id}\n"
                                          f"<b>Username:</> {bot_properties.username}")
        except Exception as err:
            logging.exception(err)
