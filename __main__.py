import asyncio

from aiogram import Bot, Dispatcher
from aiogram.client.session.middlewares.request_logging import RequestLogging, logger
from aiohttp import web


def setup_handlers(dispatcher: Dispatcher) -> None:
    """HANDLERS"""
    from handlers import setup_routers

    dispatcher.include_router(setup_routers())


def setup_middlewares(dispatcher: Dispatcher, bot: Bot) -> None:
    """MIDDLEWARE"""
    from aiogram.methods import GetUpdates
    from data.config import USE_WEBHOOK
    from middlewares.throttling import ThrottlingMiddleware

    # # Базовый Middleware Aiogram для логгирования запросов сессии.
    # # Подробности в документации https://docs.aiogram.dev/en/dev-3.x/api/session/middleware.html#
    if not USE_WEBHOOK:
        bot.session.middleware(RequestLogging(ignore_methods=[GetUpdates]))
    #
    # Классический внутренний Middleware для защита от спама. Базовые тайминги 0.5 секунд между запросами
    dispatcher.message.middleware(ThrottlingMiddleware(slow_mode_delay=0.5))


def setup_filters(dispatcher: Dispatcher) -> None:
    """FILTERS"""
    from filters import ChatPrivateFilter

    # Классический общий Filter для определения типа чата
    # Также фильтр можно ставить отдельно на каждый роутер в handlers/users/__init__
    dispatcher.message.filter(ChatPrivateFilter(chat_type=["private"]))


async def setup_aiogram(dispatcher: Dispatcher, bot: Bot) -> None:
    logger.info("Configuring aiogram")
    setup_handlers(dispatcher=dispatcher)
    setup_middlewares(dispatcher=dispatcher, bot=bot)
    setup_filters(dispatcher=dispatcher)
    logger.info("Configured aiogram")


async def aiogram_on_startup_polling(dispatcher: Dispatcher, bot: Bot) -> None:
    from utils.set_bot_commands import set_default_commands
    from utils.notify_admins import on_startup_notify

    logger.info("Starting polling")
    await bot.delete_webhook(drop_pending_updates=True)
    await setup_aiogram(bot=bot, dispatcher=dispatcher)
    await on_startup_notify(bot=bot)
    await set_default_commands(bot=bot)


async def aiogram_on_shutdown_polling(dispatcher: Dispatcher, bot: Bot):
    logger.info("Stopping polling")
    await bot.session.close()
    await dispatcher.storage.close()


async def aiohttp_on_startup(app: web.Application) -> None:
    ...


async def aiohttp_on_shutdown(app: web.Application) -> None:
    ...


async def setup_aiohttp_app(bot: Bot, dispatcher: Dispatcher) -> web.Application:
    from data.config import MAIN_WEBHOOK_SECRET_TOKEN, MAIN_WEBHOOK_PATH
    from aiogram.webhook.aiohttp_server import SimpleRequestHandler, setup_application

    await setup_aiogram(bot=bot, dispatcher=dispatcher)
    app = web.Application()
    webhook_requests_handler = SimpleRequestHandler(
        dispatcher=dispatcher,
        bot=bot,
        secret_token=MAIN_WEBHOOK_SECRET_TOKEN,
    )
    webhook_requests_handler.register(app, path=f'/{MAIN_WEBHOOK_PATH}')
    setup_application(app, dispatcher, bot=bot)
    return app


# async def get_ssl_cert():
#     import ssl
#     from data.config import WEBHOOK_SSL_CERT, WEBHOOK_SSL_PRIV
#     context = ssl.SSLContext(ssl.PROTOCOL_TLSv1_2)
#     context.load_cert_chain(WEBHOOK_SSL_CERT, WEBHOOK_SSL_PRIV)
#     return context


def main():
    """CONFIG"""
    from data.config import BOT_TOKEN, USE_WEBHOOK
    from aiogram.enums import ParseMode
    from aiogram.fsm.storage.memory import MemoryStorage

    bot = Bot(token=BOT_TOKEN, parse_mode=ParseMode.HTML)
    storage = MemoryStorage()
    dispatcher = Dispatcher(storage=storage)

    if USE_WEBHOOK:
        from data.config import MAIN_WEBHOOK_LISTENING_HOST, MAIN_WEBHOOK_LISTENING_PORT
        from utils.webhook import aiogram_on_startup_webhook, aiogram_on_shutdown_webhook

        app = asyncio.run(setup_aiohttp_app(bot=bot,
                                            dispatcher=dispatcher))
        dispatcher.startup.register(aiogram_on_startup_webhook)
        dispatcher.shutdown.register(aiogram_on_shutdown_webhook)
        web.run_app(
            app,
            handle_signals=True,
            host=MAIN_WEBHOOK_LISTENING_HOST,
            port=MAIN_WEBHOOK_LISTENING_PORT,
        )
    else:
        dispatcher.startup.register(aiogram_on_startup_polling)
        dispatcher.shutdown.register(aiogram_on_shutdown_polling)
        asyncio.run(dispatcher.start_polling(bot,  # Экземпляр бота
                                             # список типов обновлений, которые бот будет получать ['message', 'chat_member']
                                             # при dp.resolve_used_update_types() aiogram пройдётся по роутерам и сам составит список
                                             allowed_updates=['message', 'chat_member'],
                                             # закрывать сеансы бота при выключении
                                             close_bot_session=True))


if __name__ == "__main__":
    main()
