from aiogram import Dispatcher, Bot
from aiogram.client.session.middlewares.request_logging import logger


async def aiogram_on_startup_webhook(dispatcher: Dispatcher, bot: Bot) -> None:
    from data.config import MAIN_WEBHOOK_ADDRESS, MAIN_WEBHOOK_PATH, MAIN_WEBHOOK_SECRET_TOKEN
    await bot.set_webhook(
        url=f'https://{MAIN_WEBHOOK_ADDRESS}/{MAIN_WEBHOOK_PATH}',
        allowed_updates=dispatcher.resolve_used_update_types(),
        secret_token=MAIN_WEBHOOK_SECRET_TOKEN
    )
    logger.debug(f"Configured webhook: {MAIN_WEBHOOK_ADDRESS}")

    from utils.set_bot_commands import set_default_commands
    from utils.notify_admins import on_startup_notify

    logger.info("Starting webhook")

    await on_startup_notify(bot=bot)
    await set_default_commands(bot=bot)


async def aiogram_on_shutdown_webhook(dispatcher: Dispatcher, bot: Bot) -> None:
    await bot.delete_webhook()
    logger.debug(f"Stopped webhook")
