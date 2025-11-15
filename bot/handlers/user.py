from aiogram import Router, types, F
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup

from bot.core.utils.parsers import parse_reminder_time, parse_reminder_again
from bot.core.utils.helpers import fmt_datetime
from bot.services.users import UserService
from bot.services.reminders import ReminderService


router = Router()


class ReminderStates(StatesGroup):
    """Состояния для управления напоминаниями."""
    waiting_for_reminder_text = State()
    waiting_for_reminder_to_delete = State()


class ReminderAgainStates(StatesGroup):
    """Состояния для повторных напоминаний."""
    waiting_for_delay_text = State()


@router.callback_query(F.data.startswith("remind_again:"))
async def remind_again_callback(
    callback: types.CallbackQuery,
    state: FSMContext
):
    """Обрабатывает нажатие кнопки '🔁 Напомнить'."""
    reminder_id = int(callback.data.split(":")[1])
    reminder = await ReminderService.get_reminder(reminder_id)

    if not reminder:
        await callback.message.answer("❌ Напоминание не найдено.")
        return

    await callback.message.answer(
        "⏰ Когда напомнить?\n\n"
        "Пример: \n`через 10 минут`"
        "\n`через 2 часа`"
        "\n`в 18:30`",
        parse_mode="Markdown"
    )

    await state.update_data(reminder_id=reminder_id, text=reminder.text)
    await state.set_state(ReminderAgainStates.waiting_for_delay_text)

    await callback.answer()


@router.message(ReminderAgainStates.waiting_for_delay_text)
async def process_remind_again_delay(
    message: types.Message,
    state: FSMContext
):
    """ Обрабатывает ввод времени для повторного напоминания."""
    user_data = await state.get_data()
    reminder_id = user_data["reminder_id"]

    remind_at = parse_reminder_again(message.text)
    if not remind_at:
        await message.answer(
            "❌ Не удалось распознать время. Пример:\n"
            "через 10 минут или через 2 часа",
            parse_mode="Markdown"
        )
        return

    reminder = await ReminderService.update_reminder_time(
        reminder_id,
        remind_at
    )
    if not reminder:
        await message.answer("❌ Напоминание не найдено.")
        await state.clear()
        return

    ReminderService.schedule_reminder(reminder, message.from_user.id)

    await message.answer(
        f"✅ Хорошо! Напомню ещё раз.\n"
        f"🕒 {fmt_datetime(remind_at)} (Екатеринбург)"
    )
    await state.clear()


@router.message(Command("new"))
async def new_reminder(message: types.Message, state: FSMContext):
    """
    Начинает процесс создания нового напоминания.
    """
    await message.answer(
        "✍️ Напиши текст напоминания с указанием времени:\n\n"
        "**Примеры:**\n"
        "• `через 5 минут купить молоко`\n"
        "• `через 2 часа сделать домашку`\n"
        "• `в 18:30 позвонить маме`\n"
        "• `завтра в 10:00 встреча`\n"
        "• `20.12 в 15:00 забрать посылку`\n\n"
        "🕔 Я установлю напоминание по времени Екатеринбурга",
        parse_mode="Markdown"
    )
    await state.set_state(ReminderStates.waiting_for_reminder_text)


@router.message(ReminderStates.waiting_for_reminder_text)
async def process_reminder_text(message: types.Message, state: FSMContext):
    """
    Обрабатывает текст напоминания и создает его.
    """
    text = message.text.strip()
    remind_at, reminder_text = parse_reminder_time(text)

    if not remind_at or not reminder_text:
        await message.answer(
            "❌ Не удалось определить время или текст напоминания. "
            "Попробуй еще раз:\n\n"
            "**Примеры:**\n"
            "• `через 5 минут купить молоко`\n"
            "• `через 2 часа сделать домашку`\n"
            "• `в 18:30 позвонить маме`\n"
            "• `завтра в 10:00 встреча`\n"
            "• `20.12 в 15:00 забрать посылку`",
            parse_mode="Markdown"
        )
        return

    user = await UserService.ensure_user_exists(message.from_user.id)
    reminder = await ReminderService.create_reminder(
        user.id,
        reminder_text,
        remind_at
    )
    ReminderService.schedule_reminder(reminder, message.from_user.id)

    await message.answer(
        f"✅ Напоминание установлено на:\n"
        f"🕔 **{fmt_datetime(remind_at)}** (время Екатеринбурга)\n\n"
        f"📝 **Текст:** {reminder_text}",
        parse_mode="Markdown"
    )

    await state.clear()


@router.message(Command("list"))
async def list_reminders(message: types.Message):
    """
    Показывает список активных напоминаний пользователя.
    """
    user = await UserService.get_user(message.from_user.id)
    if not user:
        await message.answer("У вас пока нет напоминаний.")
        return

    reminders = await ReminderService.get_user_reminders(user.id)
    if not reminders:
        await message.answer("У вас пока нет активных напоминаний.")
        return

    text = "📋 Ваши напоминания (время Екатеринбурга):\n\n"
    for i, r in enumerate(reminders, 1):
        text += f"{i}. {r.text}\n⏰ {fmt_datetime(r.remind_at)}\nID: {r.id}\n\n"

    await message.answer(text)


@router.message(Command("delete"))
async def delete_reminder_start(message: types.Message, state: FSMContext):
    """Показывает список и просит выбрать ID для удаления"""
    user = await UserService.get_user(message.from_user.id)
    if not user:
        await message.answer("У вас пока нет напоминаний.")
        return

    reminders = await ReminderService.get_user_reminders(user.id)
    if not reminders:
        await message.answer("Нет активных напоминаний для удаления.")
        return

    text = "📋 Ваши напоминания (время Екатеринбурга):\n\n"
    for i, r in enumerate(reminders, 1):
        text += f"{i}. {r.text}\n⏰ {fmt_datetime(r.remind_at)}\nID: {r.id}\n\n"

    text += (
        "✏️ **Напишите номер ID напоминания, которое хотите удалить.**\n\n"
        "❌ Если передумали — напишите `отмена`."
    )

    await message.answer(text, parse_mode="Markdown")
    await state.set_state(ReminderStates.waiting_for_reminder_to_delete)


@router.message(ReminderStates.waiting_for_reminder_to_delete)
async def process_reminder_delete(message: types.Message, state: FSMContext):
    """
    Обрабатывает удаление напоминания по ID.
    """
    user_input = message.text.strip().lower()
    if user_input in ("отмена", "cancel", "назад"):
        await message.answer("❌ Удаление отменено.")
        await state.clear()
        return

    try:
        reminder_id = int(user_input)
    except ValueError:
        await message.answer("❌ Введите корректный ID или напишите `отмена`.")
        return

    if await ReminderService.delete_reminder(reminder_id):
        await message.answer(f"✅ Напоминание #{reminder_id} удалено.")
    else:
        await message.answer("❌ Напоминание не найдено.")
    await state.clear()
    