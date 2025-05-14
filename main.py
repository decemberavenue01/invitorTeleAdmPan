import os
import asyncio
from dotenv import load_dotenv

from aiogram import Bot, Dispatcher
from aiogram.types import ChatJoinRequest, CallbackQuery, Message, InputFile, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.filters import Command

from storage import init_db, add_user_to_db, get_all_users


# — Загрузка переменных окружения
from config import BOT_TOKEN, ADMIN_IDS, CHANNEL_ID

# — Инициализация бота и диспетчера
bot = Bot(BOT_TOKEN)
dp = Dispatcher()

# — Хэндлер для новых заявок (Chat Join Request)
async def on_join_request(req: ChatJoinRequest):
    # 1) Авто-одобрение
    await bot.approve_chat_join_request(req.chat.id, req.from_user.id)

    # 2) Сохранение пользователя в БД
    await add_user_to_db(req.from_user.id)

    # 3) Уведомление админов
    for admin_id in ADMIN_IDS:
        await bot.send_message(
            admin_id,
            f"👤 Новый запрос принят от @{req.from_user.username or req.from_user.id}"
        )

    # 4) Первое приветствие
    kb = InlineKeyboardMarkup().add(
        InlineKeyboardButton("Далее ▶️", callback_data="welcome_step2")
    )
    await bot.send_photo(
        chat_id=req.from_user.id,
        photo=InputFile("welcome.jpg"),
        caption="<b>Добро пожаловать!</b>\nЗдесь краткое описание…",
        reply_markup=kb,
        parse_mode="HTML"
    )

# — Обработка нажатия кнопки «Далее»
async def welcome_step2(callback: CallbackQuery):
    await callback.answer()

    me = await bot.get_me()
    promo_text = "здесь_твой_шаблон_текста"
    deep_link = f"https://t.me/{me.username}?start={promo_text}"

    kb = InlineKeyboardMarkup().add(
        InlineKeyboardButton("Написать мне 📩", url=deep_link)
    )
    await bot.send_photo(
        chat_id=callback.from_user.id,
        photo=InputFile("welcome2.jpg"),
        caption="<i>Вот вторая часть приветствия…</i>",
        reply_markup=kb,
        parse_mode="HTML"
    )

    # Через 60 секунд напоминание
    await asyncio.sleep(60)
    await bot.send_message(callback.from_user.id, "🔕 Не отключай уведомления этого бота.")

# — Команда админа: начало рассылки
async def cmd_broadcast_start(msg: Message):
    await msg.reply(
        "Пришли мне сообщение (текст или медиа) для рассылки всем подписчикам.\n"
        "Можно использовать HTML/Markdown и добавить кнопки."
    )

# — Обработка рассылки (ответ на предыдущее сообщение)
async def cmd_broadcast_send(msg: Message):
    users = await get_all_users()
    sent, failed = 0, 0

    for user_id in users:
        try:
            # Текст
            if msg.text:
                await bot.send_message(user_id, msg.text, parse_mode="HTML")
            # Фото
            elif msg.photo:
                file_id = msg.photo[-1].file_id
                await bot.send_photo(
                    user_id, file_id,
                    caption=msg.caption or "", parse_mode="HTML"
                )
            # Видео-кружок
            elif msg.video_note:
                await bot.send_video_note(user_id, msg.video_note.file_id)
            # Можно добавить другие типы (стикеры, видео, документы и т.д.)

            # Кнопки (если были)
            if msg.reply_markup:
                await bot.send_message(user_id, " ", reply_markup=msg.reply_markup)

            sent += 1
            await asyncio.sleep(0.05)
        except:
            failed += 1

    await msg.reply(f"Рассылка завершена ✅\nУспешно: {sent}\nНе доставлено: {failed}")

# — Регистрация хэндлеров
dp.chat_join_request.register(on_join_request)
dp.callback_query.register(welcome_step2, lambda c: c.data == "welcome_step2")
dp.message.register(cmd_broadcast_start, Command("broadcast"), lambda m: m.from_user.id in ADMIN_IDS)
dp.message.register(
    cmd_broadcast_send,
    lambda m: m.from_user.id in ADMIN_IDS
              and m.reply_to_message
              and "Пришли мне сообщение (текст или медиа)" in m.reply_to_message.text
)

# — Запуск бота и инициализация БД
async def on_startup():
    await init_db()

if __name__ == "__main__":
    dp.run_polling(bot, skip_updates=True, on_startup=on_startup)
