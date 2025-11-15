from aiogram import Router, types
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup

from bot.core.utils.helpers import fmt_datetime, is_admin
from bot.services.reminders import ReminderService
from bot.services.users import UserService


router = Router()


class BlockUser(StatesGroup):
    """Состояния для процесса блокировки пользователя."""
    waiting_for_user_id = State()
    waiting_for_reason = State()


@router.message(Command("admin"))
async def admin_panel(message: types.Message):
    """Показывает админ-панель с доступными командами."""
    if not is_admin(message.fro_user.id):
        await message.answer("❌ Доступ запрещен")
        return

    await message.answer(
        "👨‍💼 Админ панель:\n\n"
        "/admin_users - список пользователей\n"
        "/admin_reminders - все напоминания\n"
        "/block_user - заблокировать пользователя\n"
        "/unblock_user - разблокировать пользователя"
    )


@router.message(Command("admin_users"))
async def admin_users(message: types.Message):
    """Показывает список всех пользователей бота."""
    if not is_admin(message.from_user.id):
        await message.answer("❌ Доступ запрещен")
        return

    users = await UserService.get_all_users()

    text = "👥 Пользователи:\n\n"
    for user in users:
        status = "🚫 Заблокирован" if user.is_blocked else "✅ Активен"
        text += f"ID: {user.tg_id}\n"
        text += f"Статус: {status}\n"
        if user.is_blocked:
            text += f"Причина: {user.reason or 'Не указана'}\n"
        text += f"Напоминаний: {len(user.reminders)}\n\n"

    await message.answer(text)


@router.message(Command("admin_reminders"))
async def admin_reminders(message: types.Message):
    """Показывает все напоминания всех пользователей."""
    if not is_admin(message.from_user.id):
        await message.answer("❌ Доступ запрещен")
        return

    reminders = await ReminderService.get_all_reminders()

    text = "📋 Все напоминания:\n\n"
    for reminder in reminders:
        status = "✅ Отправлено" if reminder.is_sent else "⏰ Ожидает"
        text += f"ID: {reminder.id}\n"
        text += f"Пользователь: {reminder.user.tg_id}\n"
        text += f"Текст: {reminder.text}\n"
        text += f"Время: {fmt_datetime(reminder.remind_at)}\n"
        text += f"Статус: {status}\n\n"

    await message.answer(text)


@router.message(Command("block_user"))
async def block_user_start(message: types.Message, state: FSMContext):
    """Начинает процесс блокировки пользователя."""
    if not is_admin(message.from_user.id):
        await message.answer("❌ Доступ запрещен")
        return

    await message.answer("Введите ID пользователя для блокировки:")
    await state.set_state(BlockUser.waiting_for_user_id)


@router.message(BlockUser.waiting_for_user_id)
async def block_user_get_id(message: types.Message, state: FSMContext):
    """Обрабатывает ввод ID пользователя для блокировки."""
    try:
        user_id = int(message.text)
        await state.update_data(user_id=user_id)
        await message.answer("Введите причину блокировки:")
        await state.set_state(BlockUser.waiting_for_reason)
    except ValueError:
        await message.answer("❌ Некорректный ID пользователя")


@router.message(BlockUser.waiting_for_reason)
async def block_user_complete(message: types.Message, state: FSMContext):
    """Завершает блокировку пользователя с указанной причиной."""
    data = await state.get_data()
    user_id = data["user_id"]
    reason = message.text

    user = await UserService.block_user(user_id, reason)
    if user:
        await message.answer(
            f"✅ Пользователь {user_id} заблокирован\n"
            f"Причина: {reason}"
        )
    else:
        await message.answer("❌ Пользователь не найден")

    await state.clear()


@router.message(Command("unblock_user"))
async def unblock_user(message: types.Message):
    """Разблокирует пользователя по ID."""
    if not is_admin(message.from_user.id):
        await message.answer("❌ Доступ запрещен")
        return

    try:
        user_id = int(message.text.split()[1])
    except (IndexError, ValueError):
        await message.answer("Используйте: /unblock_user USER_ID")
        return

    user = await UserService.unblock_user(user_id)

    if user:
        await message.answer(f"✅ Пользователь {user_id} разблокирован")
    else:
        await message.answer("❌ Пользователь не найден или не заблокирован")
