from aiogram import Bot, Dispatcher
from aiogram.client.session.middlewares.request_logging import RequestLogging
from aiogram.enums import ParseMode
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.methods import GetUpdates

from data import config
from filters import ChatTypeFilter
from handlers.users.echo import echo_router
from handlers.users.start import start_router
from middlewares.throttling import ThrottlingMiddleware

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
# Регистрация роутеров
dp.include_routers(start_router)
dp.include_routers(echo_router)
