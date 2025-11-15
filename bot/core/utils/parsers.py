import re
from datetime import datetime, timedelta
from typing import Optional, Tuple, Union

from bot.core.utils.timezone import YEKATERINBURG_TZ


def _parse_relative_time(
    value: int,
    unit: str,
    now: datetime
) -> Optional[datetime]:
    """
    Парсит относительное время (через X минут/часов/дней).

    Args:
        value: Числовое значение (количество единиц времени)
        unit: Единица времени ('минут', 'час', 'день' и т.д.)
        now: Текущее время для отсчета

    Returns:
        datetime: Время с учетом смещения или None при ошибке
    """
    unit_lower = unit.lower()
    if "мин" in unit_lower:
        return now + timedelta(minutes=value)
    elif "час" in unit_lower:
        return now + timedelta(hours=value)
    elif "дн" in unit_lower:
        return now + timedelta(days=value)
    return None


def _parse_absolute_time(
    day: Optional[str] = None,
    month: Optional[str] = None,
    year: Optional[str] = None,
    hours: str = None,
    minutes: str = None,
    now: datetime = None,
    days_offset: int = 0
) -> Optional[datetime]:
    """
    Парсит абсолютное время с различными параметрами.

    Args:
        day: День месяца (опционально)
        month: Месяц (опционально)
        year: Год (опционально)
        hours: Часы (обязательно)
        minutes: Минуты (обязательно)
        now: Текущее время для отсчета
        days_offset: Смещение в днях (например, 1 для завтра)

    Returns:
        datetime: Распарсенное время или None при ошибке парсинга
    """
    try:
        if days_offset > 0:
            result_time = (now + timedelta(days=days_offset)).replace(
                hour=int(hours), minute=int(minutes), second=0, microsecond=0
            )
        elif year:
            result_time = datetime(
                year=int(year), month=int(month), day=int(day),
                hour=int(hours), minute=int(minutes), second=0, microsecond=0,
                tzinfo=YEKATERINBURG_TZ
            )
        elif day and month:
            current_year = now.year
            result_time = datetime(
                year=current_year, month=int(month), day=int(day),
                hour=int(hours), minute=int(minutes), second=0, microsecond=0,
                tzinfo=YEKATERINBURG_TZ
            )
            if result_time < now:
                result_time = result_time.replace(year=current_year + 1)
        else:

            result_time = now.replace(
                hour=int(hours),
                minute=int(minutes),
                second=0,
                microsecond=0
            )

            if result_time < now:
                result_time += timedelta(days=1)

        return result_time
    except (ValueError, TypeError):
        return None


def _parse_time_patterns(
    text: str,
    include_reminder_text: bool = True
) -> Union[Tuple[Optional[datetime], Optional[str]], Optional[datetime]]:
    """
    Основная функция парсинга с поддержкой обоих режимов.

    Распознает различные форматы времени в тексте:
    - Относительное время: "через 5 минут", "через 2 часа"
    - Абсолютное время: "в 18:30", "завтра в 10:00"
    - Даты: "20.12 в 15:00", "25.12.2024 в 20:00"

    Args:
        text: Текст для парсинга
        include_reminder_text: Если True - возвращает время и текст,
                              если False - возвращает только время

    Returns:
        Union[Tuple[Optional[datetime], Optional[str]], Optional[datetime]]:
        - Если include_reminder_text=True: кортеж (время, текст_напоминания)
        - Если include_reminder_text=False: время или None
    """
    now = datetime.now(YEKATERINBURG_TZ)
    text = text.strip()

    patterns = [
        {
            'pattern': (
                r"через\s+(\d+)\s*"
                r"(минут[уы]?|мин|час[а]?|часов|день|дня|дней)" +
                (r"\s+(.+)" if include_reminder_text else "")
            ),
            'handler': lambda m: (
                _parse_relative_time(int(m[1]), m[2], now),
                m[3] if include_reminder_text else None
            )
        },
        {
            'pattern': (
                r"в\s+(\d{1,2}):(\d{2})" +
                (r"\s+(.+)" if include_reminder_text else "")
            ),
            'handler': lambda m: (
                _parse_absolute_time(hours=m[1], minutes=m[2], now=now),
                m[3] if include_reminder_text else None
            )
        },
        {
            'pattern': (
                r"завтра\s+в\s+(\d{1,2}):(\d{2})" +
                (r"\s+(.+)" if include_reminder_text else "")
            ),
            'handler': lambda m: (
                _parse_absolute_time(
                    hours=m[1], minutes=m[2], now=now, days_offset=1
                ),
                m[3] if include_reminder_text else None
            )
        },
        {
            'pattern': (
                r"послезавтра\s+в\s+(\d{1,2}):(\d{2})" +
                (r"\s+(.+)" if include_reminder_text else "")
            ),
            'handler': lambda m: (
                _parse_absolute_time(
                    hours=m[1], minutes=m[2], now=now, days_offset=2
                ),
                m[3] if include_reminder_text else None
            )
        },
        {
            'pattern': (
                r"(\d{1,2})\.(\d{1,2})\.(\d{4})\s+в\s+(\d{1,2}):(\d{2})" +
                (r"\s+(.+)" if include_reminder_text else "")
            ),
            'handler': lambda m: (
                _parse_absolute_time(
                    day=m[1], month=m[2], year=m[3], hours=m[4], minutes=m[5],
                    now=now
                ),
                m[6] if include_reminder_text else None
            )
        },
        {
            'pattern': (
                r"(\d{1,2})\.(\d{1,2})\s+в\s+(\d{1,2}):(\d{2})" +
                (r"\s+(.+)" if include_reminder_text else "")
            ),
            'handler': lambda m: (
                _parse_absolute_time(
                    day=m[1], month=m[2], hours=m[3], minutes=m[4], now=now
                ),
                m[5] if include_reminder_text else None
            )
        }
    ]

    for pattern_info in patterns:
        match = re.search(pattern_info['pattern'], text, re.IGNORECASE)
        if match:
            result = pattern_info['handler'](match)
            if result[0]:
                if include_reminder_text:
                    return result
                else:
                    return result[0]

    return (None, None) if include_reminder_text else None


def parse_reminder_time(text: str) -> Tuple[Optional[datetime], Optional[str]]:
    """
    Парсит текст напоминания и возвращает время и текст.

    Args:
        text: Текст напоминания с указанием времени

    Returns:
        Tuple[Optional[datetime], Optional[str]]:
        Кортеж (время_напоминания, текст_напоминания)
        или (None, None) при ошибке
    """
    return _parse_time_patterns(text, include_reminder_text=True)


def parse_reminder_again(text: str) -> Optional[datetime]:
    """
    Парсит только время для повторного напоминания.

    Используется когда нужно установить только время повторения
    без дополнительного текста напоминания.

    Args:
        text: Текст с указанием времени (например, "через 10 минут")

    Returns:
        Optional[datetime]: Время напоминания или None при ошибке
    """
    return _parse_time_patterns(text, include_reminder_text=False)
