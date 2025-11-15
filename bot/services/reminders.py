from datetime import datetime
from typing import List, Optional

from bot.core.utils.timezone import YEKATERINBURG_TZ
from database.crud import reminders as reminder_crud
from database.models import Reminder
from database.session import AsyncSessionLocal
from worker.tasks import send_reminder


class ReminderService:
    """Сервис для работы с напоминаниями."""

    @staticmethod
    async def create_reminder(
        user_id: int,
        text: str,
        remind_at: datetime
    ) -> Reminder:
        """
        Создает новое напоминание.

        Args:
            user_id: ID пользователя в базе данных
            text: Текст напоминания
            remind_at: Время напоминания

        Returns:
            Reminder: Созданный объект напоминания
        """
        async with AsyncSessionLocal() as db:
            return await reminder_crud.create_reminder(
                db,
                user_id,
                text,
                remind_at
            )

    @staticmethod
    async def get_user_reminders(user_id: int) -> List[Reminder]:
        """
        Получает все активные напоминания пользователя.

        Args:
            user_id: ID пользователя в базе данных

        Returns:
            List[Reminder]: Список активных напоминаний
        """
        async with AsyncSessionLocal() as db:
            return await reminder_crud.get_pending_reminders(db, user_id)

    @staticmethod
    async def get_reminder(reminder_id: int) -> Optional[Reminder]:
        """
        Получает напоминание по ID.

        Args:
            reminder_id: ID напоминания

        Returns:
            Optional[Reminder]: Напоминание или None если не найдено
        """
        async with AsyncSessionLocal() as db:
            return await reminder_crud.get_reminder(db, reminder_id)

    @staticmethod
    async def delete_reminder(reminder_id: int) -> bool:
        """
        Удаляет напоминание по ID.

        Args:
            reminder_id: ID напоминания для удаления

        Returns:
            bool: True если удалено, False если не найдено
        """
        async with AsyncSessionLocal() as db:
            return await reminder_crud.delete_reminder(db, reminder_id)

    @staticmethod
    async def get_all_reminders() -> List[Reminder]:
        """
        Получает все напоминания из базы данных.

        Returns:
            List[Reminder]: Список всех напоминаний
        """
        async with AsyncSessionLocal() as db:
            return await reminder_crud.get_all_reminders(db)

    @staticmethod
    async def mark_as_sent(reminder_id: int) -> bool:
        """
        Помечает напоминание как отправленное.

        Args:
            reminder_id: ID напоминания

        Returns:
            bool: True если обновлено, False если не найдено
        """
        async with AsyncSessionLocal() as db:
            return await reminder_crud.mark_reminder_as_sent(db, reminder_id)

    @staticmethod
    async def update_reminder_time(
        reminder_id: int,
        remind_at: datetime
    ) -> Optional[Reminder]:
        """
        Обновляет время напоминания.

        Args:
            reminder_id: ID напоминания
            remind_at: Новое время напоминания

        Returns:
            Optional[Reminder]: Обновленное напоминание или None,
            если не найдено
        """
        async with AsyncSessionLocal() as db:
            return await reminder_crud.update_reminder_time(
                db,
                reminder_id,
                remind_at
            )

    @staticmethod
    def schedule_reminder(reminder: Reminder, user_tg_id: int):
        """
        Планирует отправку напоминания через Dramatiq.

        Args:
            reminder: Объект напоминания
            user_tg_id: ID пользователя в Telegram
        """
        now = datetime.now(YEKATERINBURG_TZ)
        remind_at = reminder.remind_at
        if remind_at.tzinfo is None:
            remind_at = remind_at.replace(tzinfo=YEKATERINBURG_TZ)

        time_diff = remind_at - now
        delay_seconds = max(0, time_diff.total_seconds())
        if delay_seconds > 0:
            send_reminder.send_with_options(
                args=(reminder.id, user_tg_id, reminder.text),
                delay=delay_seconds * 1000
            )
