from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from database.models import User


async def get_user(db: AsyncSession, tg_id: int) -> User | None:
    """
    Получает пользователя по ID Telegram.

    Args:
        db: Асинхронная сессия базы данных
        tg_id: ID пользователя в Telegram

    Returns:
        User | None: Объект пользователя или None если не найден
    """
    result = await db.execute(select(User).filter_by(tg_id=tg_id))
    return result.scalar_one_or_none()


async def create_user(db: AsyncSession, tg_id: int) -> User:
    """
    Создает нового пользователя в базе данных.

    Args:
        db: Асинхронная сессия базы данных
        tg_id: ID пользователя в Telegram

    Returns:
        User: Созданный объект пользователя
    """
    user = User(tg_id=tg_id)
    db.add(user)
    await db.commit()
    await db.refresh(user)
    return user


async def block_user(db: AsyncSession, tg_id: int, reason: str) -> User | None:
    """
    Блокирует пользователя с указанием причины.

    Args:
        db: Асинхронная сессия базы данных
        tg_id: ID пользователя в Telegram
        reason: Причина блокировки

    Returns:
        User | None: Заблокированный пользователь или None если не найден
    """
    user = await get_user(db, tg_id)
    if user:
        user.is_blocked = True
        user.reason = reason
        await db.commit()
    return user


async def unblock_user(db: AsyncSession, tg_id: int) -> User | None:
    """
    Разблокирует пользователя.

    Args:
        db: Асинхронная сессия базы данных
        tg_id: ID пользователя в Telegram

    Returns:
        User | None: Разблокированный пользователь или None если не найден
    """
    user = await get_user(db, tg_id)
    if user:
        user.is_blocked = False
        user.reason = None
        await db.commit()
    return user


async def get_all_users(db: AsyncSession) -> list[User]:
    """
    Получает всех пользователей из базы данных.

    Args:
        db: Асинхронная сессия базы данных

    Returns:
        List[User]: Список всех пользователей
    """
    result = await db.execute(select(User))
    return result.scalars().all()
