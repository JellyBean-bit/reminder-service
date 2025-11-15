import os

from dotenv import load_dotenv


load_dotenv()


class Settings:
    """
    Класс для хранения настроек приложения из переменных окружения.

    Атрибуты:
        BOT_TOKEN (str | None): Токен Telegram-бота.
        REDIS_URL (str | None): URL подключения к Redis.
        DATABASE_URL (str | None): URL подключения к базе данных.
        ADMINS (list[int]): Список ID администраторов.
    """
    BOT_TOKEN = os.getenv("BOT_TOKEN")
    REDIS_URL = os.getenv("REDIS_URL")
    DATABASE_URL = os.getenv("DATABASE_URL")
    ADMINS: list[int] = [
        int(x.strip()) for x in os.getenv("ADMINS", "").split(",") if x.strip()
    ]


settings = Settings()
