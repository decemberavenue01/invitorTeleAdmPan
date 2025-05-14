# handlers/admin_handler.py

import asyncio
from aiogram import Bot, Dispatcher
from aiogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.filters import Command

from config import ADMIN_IDS
from storage import get_all_users

# Флаги уведомлений (по умолчанию True)
notify_settings = {admin_id: True for admin_id in ADMIN_IDS}

def register_admin_handlers(dp: Dispatcher, bot: Bot):
    # Включить/выключить уведомления
    dp.message.register(cmd_notify_on, Command("notify_on"), lambda m: m.from_user.id in ADMIN_IDS)
    dp.message.register(cmd_notify_off, Command("notify_off"), lambda m: m.from_user.id in ADMIN_IDS)
    # Рассылка
    dp.message.register(cmd_broadcast_start, Command("broadcast"), lambda m: m.from_user.id in ADMIN_IDS)
    dp.message.register(
        cmd_broadcast_send,
        lambda m: m.from_user.id in ADMIN_IDS
                  and m.reply_to_message
                  and "✉️ Пришли мне сообщение" in m.reply_to_message.text
    )

async def cmd_notify_on(msg: Message):
    notify_settings[msg.from_user.id] = True
    await msg.reply("✅ Уведомления включены.")

async def cmd_notify_off(msg: Message):
    notify_settings[msg.from_user.id] = False
    await msg.reply("🚫 Уведомления отключены.")

async def cmd_broadcast_start(msg: Message):
    await msg.reply(
        "✉️ Пришли мне сообщение (текст или медиа) для рассылки всем пользователям.\n"
        "Можно использовать HTML/Markdown и добавить кнопки."
    )

async def cmd_broadcast_send(msg: Message):
    users = await get_all_users()
    sent = failed = 0
    for uid in users:
        try:
            # текст
            if msg.text:
                await msg.bot.send_message(uid, msg.text, parse_mode="HTML")
            # фото
            elif msg.photo:
                await msg.bot.send_photo(uid, msg.photo[-1].file_id, caption=msg.caption or "", parse_mode="HTML")
            # видео-кружок
            elif msg.video_note:
                await msg.bot.send_video_note(uid, msg.video_note.file_id)
            # другие типы при необходимости…

            # сохранить кнопки (если были)
            if msg.reply_markup:
                await msg.bot.send_message(uid, " ", reply_markup=msg.reply_markup)

            sent += 1
            await asyncio.sleep(0.05)
        except:
            failed += 1

    await msg.reply(f"Рассылка завершена ✅\nУспешно: {sent}\nНе доставлено: {failed}")
