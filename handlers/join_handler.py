from aiogram import Router, F
from aiogram.types import (
    ChatJoinRequest, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
)
from aiogram.types.input_file import FSInputFile
import asyncio
from data import approved_users
from aiogram import Bot

router = Router()

# Кнопка "УЗНАТЬ РЕЗУЛЬТАТ"
learn_more_kb = InlineKeyboardMarkup(
    inline_keyboard=[
        [InlineKeyboardButton(text="УЗНАТЬ РЕЗУЛЬТАТ", callback_data="show_result")]
    ]
)

# Кнопка "ПОЛУЧИТЬ БОНУС" — открывает ЛС с автотекстом
bonus_kb = InlineKeyboardMarkup(
    inline_keyboard=[
        [InlineKeyboardButton(
            text="ПОЛУЧИТЬ БОНУС",
            url="https://t.me/davidavidavidavidavidavidavid?start=Привет,%20я%20хочу%20получить%20бонус"
        )]
    ]
)

@router.chat_join_request()
async def handle_join_request(join_request: ChatJoinRequest, bot: Bot):
    user_id = join_request.from_user.id
    chat_id = join_request.chat.id

    # Принимаем заявку
    await bot.approve_chat_join_request(chat_id=chat_id, user_id=user_id)

    # Сохраняем пользователя в базу
    approved_users.add(user_id)

    # Отправляем приветственное сообщение
    photo = FSInputFile("media/welcome.jpg")
    await bot.send_photo(
        chat_id=user_id,
        photo=photo,
        caption="Привет! Спасибо за подписку на мой канал!",
        reply_markup=learn_more_kb
    )

@router.callback_query(F.data == "show_result")
async def show_second_message(callback: CallbackQuery, bot: Bot):
    user_id = callback.from_user.id

    await callback.answer()

    # Отправляем второе сообщение с бонусом
    try:
        photo = FSInputFile("media/welcome2.jpg")
        await bot.send_photo(
            chat_id=user_id,
            photo=photo,
            caption="У меня для тебя есть БОНУС, который...",
            reply_markup=bonus_kb  # Кнопка для открытия чата с автотекстом
        )

        # Через 60 секунд — напоминание
        await asyncio.sleep(60)
        await bot.send_message(user_id, "🔕 Не отключай уведомления этого бота.")
    except Exception as e:
        # Логируем ошибку, если не удается отправить сообщение
        print(f"Ошибка при отправке второго сообщения: {e}")
