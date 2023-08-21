from aiogram import Dispatcher, Bot
from aiogram.client.session.middlewares.request_logging import logger

from utils.generate_web_token import generate_token


async def aiogram_on_startup_webhook(dispatcher: Dispatcher, bot: Bot) -> None:
    from data.config import MAIN_WEBHOOK_ADDRESS, MAIN_WEBHOOK_PATH

    await bot.set_webhook(
        url=f'{MAIN_WEBHOOK_ADDRESS}{MAIN_WEBHOOK_PATH}',
        allowed_updates=dispatcher.resolve_used_update_types(),
        secret_token=generate_token()
    )
    logger.debug(f"Configured webhook: {MAIN_WEBHOOK_ADDRESS}")


async def aiogram_on_shutdown_webhook(dispatcher: Dispatcher, bot: Bot) -> None:
    await bot.delete_webhook()
    logger.debug(f"Stopped webhook")
