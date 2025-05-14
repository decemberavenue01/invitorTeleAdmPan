from aiogram import Router, F
from aiogram.types import Message, FSInputFile, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.filters import Command
from aiogram.enums import ParseMode
from data import admin_ids, approved_users, admin_notifications

router = Router()

# Команда /admin для входа в админ-панель
@router.message(Command("admin"))
async def admin_panel(message: Message):
    if message.from_user.id not in admin_ids:
        await message.answer("⛔️ У вас нет доступа.")
        return

    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="📢 Рассылка", callback_data="broadcast")],
        [InlineKeyboardButton(text="🔔 Уведомления: ВКЛ" if admin_notifications.get(message.from_user.id, True)
                              else "🔕 Уведомления: ВЫКЛ", callback_data="toggle_notify")]
    ])
    await message.answer("👮 Админ-панель", reply_markup=keyboard)


@router.callback_query(F.data == "toggle_notify")
async def toggle_notifications(callback):
    admin_id = callback.from_user.id
    current = admin_notifications.get(admin_id, True)
    admin_notifications[admin_id] = not current
    status = "включены" if not current else "отключены"
    await callback.message.edit_reply_markup(reply_markup=InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text=f"🔔 Уведомления: {'ВКЛ' if not current else 'ВЫКЛ'}",
                              callback_data="toggle_notify")],
        [InlineKeyboardButton(text="📢 Рассылка", callback_data="broadcast")]
    ]))
    await callback.answer(f"Уведомления {status}.")

# Запуск режима рассылки
@router.callback_query(F.data == "broadcast")
async def start_broadcast(callback):
    await callback.message.answer(
        "📨 Отправьте сообщение для рассылки (можно: фото + подпись, текст, кружок, HTML/Markdown, кнопки)"
    )
    await callback.answer()

# Обработка текста для рассылки
@router.message(F.content_type.in_({"text", "photo", "video_note"}))
async def broadcast_handler(message: Message):
    if message.from_user.id not in admin_ids:
        return

    sent_count = 0
    for user_id in approved_users:
        try:
            if message.photo:
                photo = message.photo[-1].file_id
                await message.bot.send_photo(chat_id=user_id,
                                             photo=photo,
                                             caption=message.caption,
                                             parse_mode=ParseMode.HTML)
            elif message.video_note:
                await message.bot.send_video_note(chat_id=user_id,
                                                  video_note=message.video_note.file_id)
            else:
                await message.bot.send_message(chat_id=user_id,
                                               text=message.text,
                                               parse_mode=ParseMode.HTML)
            sent_count += 1
        except Exception:
            continue

    await message.answer(f"✅ Рассылка завершена. Отправлено {sent_count} пользователям.")
