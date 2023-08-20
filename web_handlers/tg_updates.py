import secrets

import aiohttp.web
import aiojobs
from aiogram import Bot, Dispatcher, types
from aiohttp import web

from data import config

tg_updates_app = web.Application()


async def process_update(upd: types.Update, bot: Bot, dispatcher: Dispatcher) -> None:
    Bot.set_current(bot)  # Нужно переделать
    await dispatcher.feed_webhook_update(bot, upd)


async def execute(req: web.Request) -> web.Response:
    if not secrets.compare_digest(
            req.headers.get("X-Telegram-Bot-Api-Secret-Token", ""),
            config.MAIN_WEBHOOK_SECRET_TOKEN,
    ):
        raise aiohttp.web.HTTPNotFound()
    if not secrets.compare_digest(req.match_info["token"], config.BOT_TOKEN):
        raise aiohttp.web.HTTPNotFound()
    scheduler: aiojobs.Scheduler = req.app["scheduler"]
    if scheduler.pending_count >= config.MAX_UPDATES_IN_QUEUE:
        raise web.HTTPTooManyRequests()
    if scheduler.closed:
        raise web.HTTPServiceUnavailable(reason="Closed queue")
    await scheduler.spawn(
            process_update(
                    types.Update(**(await req.json())), req.app["bot"], req.app["dispatcher"]
            )
    )
    return web.Response()


tg_updates_app.add_routes([web.post("/bot/{token}", execute)])
