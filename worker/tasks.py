import asyncio

import dramatiq

from bot.keyboards.reply import reply_keyboard
from bot.core.loader import bot
from database.session import AsyncSessionLocal
from database.crud.reminders import get_reminder, mark_reminder_as_sent
from database.crud.users import get_user


@dramatiq.actor
def send_reminder(reminder_id: int, user_id: int, text: str):
    """
    Фоновая задача для отправки напоминания пользователю.

    Args:
        reminder_id: ID напоминания в базе данных
        user_id: ID пользователя в Telegram
        text: Текст напоминания для отправки
    """

    async def send():
        """
        Асинхронная функция отправки сообщения с напоминанием.
        """
        try:
            async with AsyncSessionLocal() as db:
                user = await get_user(db, user_id)
                if user.is_blocked:
                    return

                reminder = await get_reminder(db, reminder_id)
                if not reminder or reminder.is_sent:
                    return

                keyboard = reply_keyboard(reminder_id)

                await bot.send_message(
                    chat_id=user_id,
                    text=f"🔔 Напоминание: {text}",
                    reply_markup=keyboard
                )

                await mark_reminder_as_sent(db, reminder_id)

        except Exception as e:
            print(f"DRAMATIQ: Ошибка отправки: {e}")

    asyncio.run(send())
