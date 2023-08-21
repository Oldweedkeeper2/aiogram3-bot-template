# Тут вы можете указать Id всех админов, которым должны приходить сообщения при запуске бота.
# Само сообщение вы можете увидеть | изменить в файле utils/notify_admins.py

import subprocess

from environs import Env

admins = [
    123456789,
]
VERSION = subprocess.check_output(["git", "describe", "--always"]).strip().decode()

env = Env()
env.read_env()

BOT_TOKEN: str = env.str("BOT_TOKEN")

LOGGING_LEVEL: int = env.int("LOGGING_LEVEL", 10)

USE_WEBHOOK: bool = env.bool("USE_WEBHOOK", False)

if USE_WEBHOOK:
    MAIN_WEBHOOK_ADDRESS: str = env.str("MAIN_WEBHOOK_ADDRESS")
    MAIN_WEBHOOK_SECRET_TOKEN: str = env.str("MAIN_WEBHOOK_SECRET_TOKEN")
    
    MAIN_WEBHOOK_PATH: str = env.str("MAIN_WEBHOOK_PATH")
    MAIN_WEBHOOK_LISTENING_HOST: str = env.str("MAIN_WEBHOOK_LISTENING_HOST")
    MAIN_WEBHOOK_LISTENING_PORT: int = env.int("MAIN_WEBHOOK_LISTENING_PORT")

    MAX_UPDATES_IN_QUEUE: int = env.int("MAX_UPDATES_IN_QUEUE", 100)


    # Secret key to validate requests from Telegram (optional)
    WEBHOOK_SECRET = "my-secret"
    # Base URL for webhook will be used to generate webhook URL for Telegram,
    # in this example it is used public DNS with HTTPS support
    BASE_WEBHOOK_URL = "https://aiogram.dev/"

USE_CUSTOM_API_SERVER: bool = env.bool("USE_CUSTOM_API_SERVER", False)

if USE_CUSTOM_API_SERVER:
    CUSTOM_API_SERVER_IS_LOCAL: bool = env.bool("CUSTOM_API_SERVER_IS_LOCAL")
    CUSTOM_API_SERVER_BASE: str = env.str("CUSTOM_API_SERVER_BASE")
    CUSTOM_API_SERVER_FILE: str = env.str("CUSTOM_API_SERVER_FILE")
