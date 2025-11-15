import asyncio

from aiogram.types import BotCommand

from bot.core.loader import bot, dp
from bot.core.middlewares.block_check import BlockCheckMiddleware
from bot.handlers import admin, common, user
from database.session import init_db


async def main():
    """
    Основная функция запуска бота.

    Инициализирует middleware, регистрирует роутеры,
    устанавливает команды бота и запускает опрос сервера.
    """
    dp.message.middleware(BlockCheckMiddleware())

    dp.include_router(common.router)
    dp.include_router(user.router)
    dp.include_router(admin.router)

    await bot.set_my_commands([
        BotCommand(command="start", description="Начать"),
        BotCommand(command="new", description="Создать напоминание"),
        BotCommand(command="list", description="Список напоминаний"),
        BotCommand(command="delete", description="Удалить напоминание"),
    ])

    await init_db()

    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
