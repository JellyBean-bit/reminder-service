from datetime import datetime

from bot.core.config import settings
from bot.core.utils.timezone import YEKATERINBURG_TZ


def fmt_datetime(dt: datetime) -> str:
    """
    Форматирует datetime в строку с учетом временной зоны Екатеринбурга.

    Args:
        dt: Объект datetime для форматирования

    Returns:
        str: Отформатированная строка в формате 'дд.мм.гггг чч:мм'
    """
    return dt.replace(tzinfo=YEKATERINBURG_TZ).strftime("%d.%m.%Y %H:%M")


def is_admin(user_id: int) -> bool:
    """
    Проверяет, является ли пользователь администратором.

    Args:
        user_id: ID пользователя Telegram для проверки

    Returns:
        bool: True если пользователь администратор, иначе False
    """
    if not hasattr(settings, 'ADMINS') or not settings.ADMINS:
        return False

    return user_id in settings.ADMINS
