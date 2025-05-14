# handlers/join_handler.py

import asyncio
from aiogram import Bot, Dispatcher
from aiogram.types import ChatJoinRequest, CallbackQuery, InputFile, InlineKeyboardMarkup, InlineKeyboardButton

from config import ADMIN_IDS
from storage import add_user_to_db
from handlers.admin_handler import notify_settings

async def on_join_request(req: ChatJoinRequest, bot: Bot):
    # 1) Авто-одобрение
    await bot.approve_chat_join_request(req.chat.id, req.from_user.id)

    # 2) Сохранение пользователя
    await add_user_to_db(req.from_user.id)

    # 3) Уведомление админов
    for admin_id in ADMIN_IDS:
        if notify_settings.get(admin_id, True):
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

async def on_welcome_step2(callback: CallbackQuery, bot: Bot):
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

    await asyncio.sleep(60)
    await bot.send_message(callback.from_user.id, "🔕 Не отключай уведомления этого бота.")

def register_join_handlers(dp: Dispatcher):
    """
    Регистрирует хэндлеры автоприёма заявок и callback.
    Aiogram сам инжектит Bot и ChatJoinRequest/CallbackQuery по типизации.
    """
    dp.chat_join_request.register(on_join_request)
    dp.callback_query.register(on_welcome_step2, lambda c: c.data == "welcome_step2")
