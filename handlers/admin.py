import os
import json
from aiogram import Router, F
from aiogram.types import (
    Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton,
    InputFile
)
from aiogram.filters import Command
from aiogram import Bot
from dotenv import load_dotenv

# Загружаем переменные из .env
load_dotenv()
ADMINS = list(map(int, os.getenv("ADMINS", "").split(",")))

router = Router()

# Проверка на админа
def is_admin(user_id: int) -> bool:
    return user_id in ADMINS

# Команда для запуска рассылки
@router.message(Command("broadcast"))
async def start_broadcast(message: Message, bot: Bot):
    if not is_admin(message.from_user.id):
        return await message.answer("⛔ У вас нет доступа.")

    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="📝 HTML", callback_data="format_html")],
        [InlineKeyboardButton(text="🔤 Markdown", callback_data="format_markdown")]
    ])
    await message.answer("📌 Выбери формат разметки текста:", reply_markup=keyboard)

# Выбор формата
@router.callback_query(F.data.startswith("format_"))
async def choose_format(callback: CallbackQuery, bot: Bot):
    fmt = callback.data.split("_")[1]
    await bot.session.storage.set_data(user=callback.from_user.id, data={
        "step": "awaiting_text",
        "parse_mode": fmt
    })
    await callback.message.edit_text("✍️ Отправь текст рассылки (можно с разметкой):")

# Обработка этапов рассылки
@router.message()
async def handle_broadcast_steps(message: Message, bot: Bot):
    user_id = message.from_user.id
    if not is_admin(user_id):
        return

    state = await bot.session.storage.get_data(user=user_id)
    if not state or "step" not in state:
        return

    step = state["step"]

    # Шаг 1 — Текст
    if step == "awaiting_text":
        await bot.session.storage.set_data(user=user_id, data={
            "step": "awaiting_media",
            "text": message.html_text,
            "parse_mode": state.get("parse_mode", "html")
        })
        return await message.answer("📎 Пришли фото или видеокружок (или отправь `пропустить`)")

    # Шаг 2 — Медиа
    elif step == "awaiting_media":
        data = await bot.session.storage.get_data(user=user_id)
        text = data.get("text")
        parse_mode = data.get("parse_mode", "html")

        media_id = None
        media_type = None

        if message.photo:
            media_id = message.photo[-1].file_id
            media_type = "photo"
        elif message.video_note:
            media_id = message.video_note.file_id
            media_type = "video_note"
        elif message.text and message.text.lower() == "пропустить":
            media_type = "none"

        await bot.session.storage.set_data(user=user_id, data={
            "step": "awaiting_button",
            "text": text,
            "media_id": media_id,
            "media_type": media_type,
            "parse_mode": parse_mode
        })

        return await message.answer("🔘 Пришли кнопку в формате:\n\n`Текст кнопки - https://example.com`\n\nИли `нет` если не нужна", parse_mode="Markdown")

    # Шаг 3 — Кнопка и рассылка
    elif step == "awaiting_button":
        data = await bot.session.storage.get_data(user=user_id)
        text = data.get("text")
        media_id = data.get("media_id")
        media_type = data.get("media_type")
        parse_mode = data.get("parse_mode", "html").upper()

        button = None
        if "-" in message.text and "http" in message.text:
            parts = message.text.split("-", 1)
            btn_text = parts[0].strip()
            btn_url = parts[1].strip()
            button = InlineKeyboardMarkup(inline_keyboard=[
                [InlineKeyboardButton(text=btn_text, url=btn_url)]
            ])

        await message.answer("✅ Рассылка началась!")

        # Загрузка базы пользователей
        USER_FILE = "data/users.json"
        try:
            with open(USER_FILE, "r") as f:
                users = json.load(f)
        except:
            users = []

        success = 0
        fail = 0

        for uid in users:
            try:
                if media_type == "photo":
                    await bot.send_photo(uid, photo=media_id, caption=text, reply_markup=button, parse_mode=parse_mode)
                elif media_type == "video_note":
                    await bot.send_video_note(uid, video_note=media_id)
                    await bot.send_message(uid, text, reply_markup=button, parse_mode=parse_mode)
                else:
                    await bot.send_message(uid, text, reply_markup=button, parse_mode=parse_mode)

                success += 1
            except:
                fail += 1

        await message.answer(f"📬 Рассылка завершена.\n✅ Успешно: {success}\n❌ Ошибок: {fail}")
        await bot.session.storage.set_data(user=user_id, data={})
