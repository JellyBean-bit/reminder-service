from typing import Optional

from database.session import AsyncSessionLocal
from database.crud import users as user_crud
from database.models import User


class UserService:
    """Сервис для работы с пользователями."""

    @staticmethod
    async def ensure_user_exists(tg_id: int) -> User:
        """
        Создает пользователя если не существует, иначе возвращает существующего

        Args:
            tg_id: ID пользователя в Telegram

        Returns:
            User: Объект пользователя
        """
        async with AsyncSessionLocal() as db:
            user = await user_crud.get_user(db, tg_id)
            if not user:
                user = await user_crud.create_user(db, tg_id)
            return user

    @staticmethod
    async def get_user(tg_id: int) -> Optional[User]:
        """
        Получает пользователя по ID Telegram.

        Args:
            tg_id: ID пользователя в Telegram

        Returns:
            Optional[User]: Объект пользователя или None если не найден
        """
        async with AsyncSessionLocal() as db:
            return await user_crud.get_user(db, tg_id)

    @staticmethod
    async def is_user_blocked(tg_id: int) -> bool:
        """
        Проверяет, заблокирован ли пользователь.

        Args:
            tg_id: ID пользователя в Telegram

        Returns:
            bool: True если пользователь заблокирован,
            False если нет или не найден
        """
        async with AsyncSessionLocal() as db:
            user = await user_crud.get_user(db, tg_id)
            return user.is_blocked if user else False

    @staticmethod
    async def block_user(tg_id: int, reason: str) -> Optional[User]:
        """
        Блокирует пользователя с указанием причины.

        Args:
            tg_id: ID пользователя в Telegram
            reason: Причина блокировки

        Returns:
            Optional[User]: Заблокированный пользователь или
            None если не найден
        """
        async with AsyncSessionLocal() as db:
            return await user_crud.block_user(db, tg_id, reason)

    @staticmethod
    async def unblock_user(tg_id: int) -> Optional[User]:
        """
        Разблокирует пользователя.

        Args:
            tg_id: ID пользователя в Telegram

        Returns:
            Optional[User]: Разблокированный пользователь или None,
            если не найден
        """
        async with AsyncSessionLocal() as db:
            return await user_crud.unblock_user(db, tg_id)

    @staticmethod
    async def get_all_users() -> list[User]:
        """
        Получает всех пользователей из базы данных.

        Returns:
            List[User]: Список всех пользователей
        """
        async with AsyncSessionLocal() as db:
            return await user_crud.get_all_users(db)
