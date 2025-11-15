from typing import Any, Awaitable, Callable, Dict

from aiogram import BaseMiddleware
from aiogram.types import Message

from bot.services.users import UserService


class BlockCheckMiddleware(BaseMiddleware):
    """
    Middleware для проверки блокировки пользователей.

    Проверяет, заблокирован ли пользователь перед обработкой сообщения.
    Если пользователь заблокирован, сообщение не передается дальше по цепочке.
    """

    async def __call__(
        self,
        handler: Callable[[Message, Dict[str, Any]], Awaitable[Any]],
        event: Message,
        data: Dict[str, Any]
    ) -> Any:
        """
        Обрабатывает входящее сообщение
        и проверяет статус блокировки пользователя.

        Args:
            handler: Следующий обработчик в цепочке middleware
            event: Объект сообщения от пользователя
            data: Данные контекста

        Returns:
            Any: Результат обработки handler или None,
            если пользователь заблокирован
        """
        user = await UserService.get_user(event.from_user.id)

        if user and user.is_blocked:
            await event.answer(
                f"❌ Вы заблокированы!\n"
                f"Причина: {user.reason or 'Не указана'}\n\n"
                f"По вопросам разблокировки обратитесь к администратору."
            )
            return

        return await handler(event, data)
