import secrets
import subprocess

from environs import Env

# Список идентификаторов администраторов, которым будут отправляться уведомления при запуске бота
admins = [
    123456789,
]

# Получение текущей версии из системы контроля версий Git
VERSION = subprocess.check_output(["git", "describe", "--always"]).strip().decode()

# Инициализация объекта для работы с переменными окружения
env = Env()
env.read_env()

# Токен бота
BOT_TOKEN: str = env.str("BOT_TOKEN")

# Уровень логирования
LOGGING_LEVEL: int = env.int("LOGGING_LEVEL", 10)

# Использовать ли вебхук
USE_WEBHOOK: bool = env.bool("USE_WEBHOOK", False)

# Использовать ли SSL
USE_SSL: bool = env.bool("USE_SSL", False)

# Если используется вебхук
if USE_WEBHOOK:
    # Основной адрес вебхука
    MAIN_WEBHOOK_ADDRESS: str = env.str("MAIN_WEBHOOK_ADDRESS")

    # Секретный токен для вебхука
    MAIN_WEBHOOK_SECRET_TOKEN: str = secrets.token_urlsafe(32)

    # Путь к вебхуку
    MAIN_WEBHOOK_PATH: str = env.str("MAIN_WEBHOOK_PATH")

    # Хост для прослушивания вебхука
    MAIN_WEBHOOK_LISTENING_HOST: str = env.str("MAIN_WEBHOOK_LISTENING_HOST")

    # Порт для прослушивания вебхука
    MAIN_WEBHOOK_LISTENING_PORT: int = env.int("MAIN_WEBHOOK_LISTENING_PORT")

    # Максимальное количество обновлений в очереди
    MAX_UPDATES_IN_QUEUE: int = env.int("MAX_UPDATES_IN_QUEUE", 100)

    # Если используется SSL
    if USE_SSL:

        # Путь к SSL-сертификату
        WEBHOOK_SSL_CERT: str = env.str("WEBHOOK_SSL_CERT")

        # Путь к приватному ключу SSL
        WEBHOOK_SSL_PRIV: str = env.str("WEBHOOK_SSL_PRIV")

# Использовать ли пользовательский сервер API
USE_CUSTOM_API_SERVER: bool = env.bool("USE_CUSTOM_API_SERVER", False)

# Если используется пользовательский сервер API
if USE_CUSTOM_API_SERVER:

    # Является ли сервер API локальным
    CUSTOM_API_SERVER_IS_LOCAL: bool = env.bool("CUSTOM_API_SERVER_IS_LOCAL")

    # Базовый адрес пользовательского сервера API
    CUSTOM_API_SERVER_BASE: str = env.str("CUSTOM_API_SERVER_BASE")

    # Файл пользовательского сервера API
    CUSTOM_API_SERVER_FILE: str = env.str("CUSTOM_API_SERVER_FILE")
