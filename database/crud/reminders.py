from datetime import datetime

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from database.models import Reminder


async def create_reminder(
    db: AsyncSession,
    user_id: int,
    text: str,
    remind_at: datetime
) -> Reminder:
    """
    Создает новое напоминание в базе данных.

    Args:
        db: Сессия базы данных
        user_id: ID пользователя
        text: Текст напоминания
        remind_at: Время напоминания

    Returns:
        Reminder: Созданный объект напоминания
    """
    reminder = Reminder(user_id=user_id, text=text, remind_at=remind_at)
    db.add(reminder)
    await db.commit()
    await db.refresh(reminder)
    return reminder


async def get_pending_reminders(
    db: AsyncSession,
    user_id: int
) -> list[Reminder]:
    """
    Получает все активные напоминания пользователя.

    Args:
        db: Сессия базы данных
        user_id: ID пользователя

    Returns:
        List[Reminder]: Список активных напоминаний, отсортированных по времени
    """
    result = await db.execute(
        select(Reminder)
        .filter(Reminder.user_id == user_id, Reminder.is_sent == False)
        .order_by(Reminder.remind_at)
    )
    return result.scalars().all()


async def get_reminder(db: AsyncSession, reminder_id: int) -> Reminder | None:
    """
    Получает напоминание по ID.

    Args:
        db: Сессия базы данных
        reminder_id: ID напоминания

    Returns:
        Reminder: Объект напоминания или None если не найдено
    """
    result = await db.execute(select(Reminder).filter_by(id=reminder_id))
    return result.scalar_one_or_none()


async def delete_reminder(db: AsyncSession, reminder_id: int) -> bool:
    """
    Удаляет напоминание по ID.

    Args:
        db: Асинхронная сессия базы данных
        reminder_id: ID напоминания для удаления

    Returns:
        bool: True если удалено, False если не найдено
    """
    reminder = await get_reminder(db, reminder_id)
    if reminder:
        await db.delete(reminder)
        await db.commit()
        return True
    return False


async def get_all_reminders(db: AsyncSession) -> list[Reminder]:
    """
    Получает все напоминания из базы данных.

    Args:
        db: Асинхронная сессия базы данных

    Returns:
        List[Reminder]: Список всех напоминаний
    """
    result = await db.execute(select(Reminder))
    return result.scalars().all()


async def mark_reminder_as_sent(db: AsyncSession, reminder_id: int) -> bool:
    """
    Помечает напоминание как отправленное.

    Args:
        db: Асинхронная сессия базы данных
        reminder_id: ID напоминания

    Returns:
        bool: True если обновлено, False если не найдено
    """
    reminder = await get_reminder(db, reminder_id)
    if reminder:
        reminder.is_sent = True
        await db.commit()
        return True
    return False


async def update_reminder_time(
    db: AsyncSession,
    reminder_id: int,
    remind_at: datetime
) -> Reminder | None:
    """
    Обновляет время напоминания и сбрасывает статус отправки.

    Args:
        db: Асинхронная сессия базы данных
        reminder_id: ID напоминания
        remind_at: Новое время напоминания

    Returns:
        Reminder | None: Обновленное напоминание или None если не найдено
    """
    reminder = await get_reminder(db, reminder_id)
    if reminder:
        reminder.remind_at = remind_at
        reminder.is_sent = False
        await db.commit()
        await db.refresh(reminder)
        return reminder
    return None
