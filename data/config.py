import os

from dotenv import load_dotenv

load_dotenv()

BOT_TOKEN = str(os.getenv("BOT_TOKEN"))

# Тут вы можете указать Id всех админов, которым должны приходить сообщения при запуске бота.
# Само сообщение вы можете увидеть | изменить в файле utils/notify_admins.py
admins = [
    123456789,
]
