import asyncio

from aiogram import Bot, Dispatcher
from aiogram.client.session.middlewares.request_logging import RequestLogging
from aiogram.enums import ParseMode
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.methods import GetUpdates

from data import config
from filters import ChatTypeFilter
from handlers import setup_routers
from middlewares.throttling import ThrottlingMiddleware


async def on_startup(bot: Bot) -> None:
    from utils.set_bot_commands import set_default_commands
    from utils.notify_admins import on_startup_notify
    
    await on_startup_notify(bot)
    await set_default_commands(bot)


async def main():
    """CONFIG"""
    
    bot = Bot(token=config.BOT_TOKEN, parse_mode=ParseMode.HTML)
    storage = MemoryStorage()
    dp = Dispatcher(storage=storage)
    
    """MIDDLEWARE"""
    
    # Базовый Middleware Aiogram для логгирования запросов сессии.
    # Подробности в документации https://docs.aiogram.dev/en/dev-3.x/api/session/middleware.html#
    bot.session.middleware(RequestLogging(ignore_methods=[GetUpdates]))
    
    # Классический Middleware для защита от спама. Базовые тайминги 0.5 секунд между запросами
    dp.message.middleware(ThrottlingMiddleware(slow_mode_delay=0.5))
    
    """FILTERS"""
    # Классический Filter для определения типа чата
    dp.message.filter(ChatTypeFilter(chat_type=["private"]))
    
    """ROUTERS"""
    # Регистрация роутера
    dp.include_router(setup_routers())
    
    # Запускаем бота и пропускаем все накопленные входящие
    # Да, этот метод можно вызвать даже если у вас поллинг
    dp.startup.register(on_startup)
    
    # await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot,  # Экземпляр бота
                           # список типов обновлений, которые бот будет получать ['message', 'chat_member']
                           # при dp.resolve_used_update_types() aiogram пройдётся по роутерам и сам составит список
                           allowed_updates=['message', 'chat_member'],
                           # закрывать сеансы бота при выключении
                           close_bot_session=True)


if __name__ == "__main__":
    asyncio.run(main())
