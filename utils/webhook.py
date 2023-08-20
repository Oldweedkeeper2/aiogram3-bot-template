from aiogram import Dispatcher, Bot
from aiogram.client.session.middlewares.request_logging import logger

from data import config


async def aiogram_on_startup_webhook(dispatcher: Dispatcher, bot: Bot) -> None:

    webhook_url = config.MAIN_WEBHOOK_ADDRESS
    await bot.set_webhook(
            url=webhook_url,
            allowed_updates=dispatcher.resolve_used_update_types(),
    )
    logger.debug(f"Configured webhook: {webhook_url}")


async def aiogram_on_shutdown_webhook(dispatcher: Dispatcher, bot: Bot) -> None:
    await bot.delete_webhook()
    logger.debug(f"Stopped webhook")
