import asyncio

import aiojobs
from aiogram import Bot, Dispatcher
from aiogram.client.session.middlewares.request_logging import RequestLogging, logger
from aiogram.enums import ParseMode
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.methods import GetUpdates
from aiogram.webhook.aiohttp_server import setup_application
from aiohttp import web

import web_handlers
from data import config
from filters import ChatTypeFilter
from handlers import setup_routers
from middlewares.throttling import ThrottlingMiddleware
from utils.webhook import aiogram_on_startup_webhook, aiogram_on_shutdown_webhook


def setup_handlers(dispatcher: Dispatcher) -> None:
    """HANDLERS"""
    
    dispatcher.include_router(setup_routers())


def setup_middlewares(dispatcher: Dispatcher, bot: Bot) -> None:
    """MIDDLEWARE"""
    
    # # Базовый Middleware Aiogram для логгирования запросов сессии.
    # # Подробности в документации https://docs.aiogram.dev/en/dev-3.x/api/session/middleware.html#
    if not config.USE_WEBHOOK:
        bot.session.middleware(RequestLogging(ignore_methods=[GetUpdates]))
    #
    # Классический внутренний Middleware для защита от спама. Базовые тайминги 0.5 секунд между запросами
    dispatcher.message.middleware(ThrottlingMiddleware(slow_mode_delay=0.5))


def setup_filters(dispatcher: Dispatcher) -> None:
    """FILTERS"""
    # Классический общий Filter для определения типа чата
    # Также фильтр можно ставить отдельно на каждый роутер в handlers/users/__init__
    dispatcher.message.filter(ChatTypeFilter(chat_type=["private"]))


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
    dispatcher: Dispatcher = app["dispatcher"]
    workflow_data = {"app": app, "dispatcher": dispatcher}
    if "bot" in app:
        workflow_data["bot"] = app["bot"]
    await dispatcher.emit_startup(**workflow_data)


async def aiohttp_on_shutdown(app: web.Application) -> None:
    dispatcher: Dispatcher = app["dispatcher"]
    for i in [app, *app._subapps]:  # Нужно переделать
        if "scheduler" in i:
            scheduler: aiojobs.Scheduler = i["scheduler"]
            scheduler._closed = True
            while scheduler.pending_count != 0:
                dispatcher["aiogram_logger"].info(
                        f"Waiting for {scheduler.pending_count} tasks to complete"
                )
                await asyncio.sleep(1)
    workflow_data = {"app": app, "dispatcher": dispatcher}
    if "bot" in app:
        workflow_data["bot"] = app["bot"]
    await dispatcher.emit_shutdown(**workflow_data)


async def setup_aiohttp_app(bot: Bot, dispatcher: Dispatcher) -> web.Application:
    scheduler = aiojobs.Scheduler()
    app = web.Application()
    subapps: list[tuple[str, web.Application]] = [
        ("/tg/webhooks/", web_handlers.tg_updates_app),
    ]
    for prefix, subapp in subapps:
        subapp["bot"] = bot
        subapp["dispatcher"] = dispatcher
        subapp["scheduler"] = scheduler
        app.add_subapp(prefix, subapp)
    app["bot"] = bot
    app["dispatcher"] = dispatcher
    app["scheduler"] = scheduler
    app.on_startup.append(aiohttp_on_startup)
    app.on_shutdown.append(aiohttp_on_shutdown)
    return app


def main():
    """CONFIG"""
    
    bot = Bot(token=config.BOT_TOKEN, parse_mode=ParseMode.HTML)
    storage = MemoryStorage()
    dispatcher = Dispatcher(storage=storage)
    if config.USE_WEBHOOK:
        dispatcher.startup.register(aiogram_on_startup_webhook)
        dispatcher.shutdown.register(aiogram_on_shutdown_webhook)
        app = asyncio.run(setup_aiohttp_app(bot, dispatcher))
        web.run_app(
                app,
                handle_signals=True,
                host=config.MAIN_WEBHOOK_LISTENING_HOST,
                port=config.MAIN_WEBHOOK_LISTENING_PORT,
        )
        setup_application(app, dispatcher, bot=bot)
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
