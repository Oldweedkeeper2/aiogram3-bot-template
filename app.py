import asyncio

from aiogram import Bot

from loader import bot, dp


async def on_startup(bot: Bot) -> None:
    from utils.set_bot_commands import set_default_commands
    from utils.notify_admins import on_startup_notify
    
    await on_startup_notify(bot)
    await set_default_commands(bot)


async def main():
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
