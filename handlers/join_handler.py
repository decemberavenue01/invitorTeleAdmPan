from aiogram import Router, Bot, F
from aiogram.types import ChatJoinRequest, InlineKeyboardMarkup, InlineKeyboardButton, FSInputFile
from aiogram.types import CallbackQuery, InputMediaPhoto
from aiogram.utils.formatting import Bold
import asyncio
import os
from dotenv import load_dotenv

load_dotenv()

router = Router()

# Приветственное сообщение
WELCOME_TEXT = "👋 Добро пожаловать в наш канал!\n\nНажми кнопку ниже, чтобы продолжить 👇"
WELCOME_BUTTON = InlineKeyboardMarkup(
    inline_keyboard=[
        [InlineKeyboardButton(text="Продолжить", callback_data="continue")]
    ]
)

@router.chat_join_request()
async def handle_join_request(event: ChatJoinRequest, bot: Bot):
    # Автоматически одобряем заявку
    await bot.approve_chat_join_request(chat_id=event.chat.id, user_id=event.from_user.id)

    # Отправляем приветственное сообщение с картинкой и кнопкой
    photo = FSInputFile("media/welcome.jpg")  # убедись, что картинка лежит в папке media
    await bot.send_photo(
        chat_id=event.from_user.id,
        photo=photo,
        caption=WELCOME_TEXT,
        reply_markup=WELCOME_BUTTON
    )
    from handlers.admin import load_notify_config, ADMIN_IDS

    # Рассылаем уведомления админам (если включено)
    config = load_notify_config()
    text = f"📥 Новая заявка от @{event.from_user.username or 'пользователя'} (ID: {event.from_user.id})"

    for admin_id in ADMIN_IDS:
        if config.get(str(admin_id), True):  # если не отключены
            try:
                await bot.send_message(chat_id=admin_id, text=text)
            except:
                pass  # если бот не может написать админу


# Заменяем user_id на свой — вставь сюда свой Telegram username без @
YOUR_USERNAME = os.getenv("OWNER_USERNAME")
OWNER_ID = int(os.getenv("OWNER_ID"))


# Текст и шаблон для второго сообщения
SECOND_TEXT = "Вот дополнительная информация. Нажми кнопку ниже, чтобы написать нам!"
TEMPLATE_TEXT = "Здравствуйте, у меня есть вопрос по поводу вступления..."

SECOND_BUTTON = InlineKeyboardMarkup(
    inline_keyboard=[
        [InlineKeyboardButton(
            text="Написать в ЛС",
            url=f"https://t.me/{YOUR_USERNAME}?start={TEMPLATE_TEXT.replace(' ', '%20')}"
        )]
    ]
)

@router.callback_query(F.data == "continue")
async def handle_continue_button(callback: CallbackQuery, bot: Bot):
    user_id = callback.from_user.id

    # Отправка второго сообщения
    photo = FSInputFile("media/welcome2.jpg")
    await bot.send_photo(
        chat_id=user_id,
        photo=photo,
        caption=SECOND_TEXT,
        reply_markup=SECOND_BUTTON
    )

    # Ожидание 60 секунд
    await asyncio.sleep(60)

    # Отправка напоминания
    await bot.send_message(
        chat_id=user_id,
        text="🔕 Не отключай уведомления этого бота."
    )

    # Удаляем спиннер "loading..." у кнопки
    await callback.answer()
