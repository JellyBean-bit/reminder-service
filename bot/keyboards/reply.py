from aiogram import types


def reply_keyboard(reminder_id: int) -> types.InlineKeyboardMarkup:
    """
    Создает инлайн-клавиатуру с кнопкой повтора напоминания.

    Args:
        reminder_id: ID напоминания для callback_data

    Returns:
        types.InlineKeyboardMarkup: Готовая клавиатура с кнопкой
    """
    keyboard = types.InlineKeyboardMarkup(
                    inline_keyboard=[
                        [
                            types.InlineKeyboardButton(
                                text="🔁 Повторить",
                                callback_data=f"remind_again:{reminder_id}"
                            )
                        ]
                    ]
                )
    return keyboard
