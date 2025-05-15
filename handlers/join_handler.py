from aiogram import Router, F, Bot
from aiogram.types import (
    ChatJoinRequest, Message, InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery
)
from aiogram.types.input_file import FSInputFile
from urllib.parse import quote
import asyncio
from data import approved_users

router = Router()

# Имя бота и владельца
BOT_USERNAME = "invitorTeleAdmPan_bot"          # Без @
OWNER_USERNAME = "davidavidavidavidavidavidavid"  # 🔁 ЗАМЕНИ на свой Telegram username без @

# Кнопка "УЗНАТЬ РЕЗУЛЬТАТ" с callback_data
def learn_more_kb(user_id: int) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(
                text="УЗНАТЬ РЕЗУЛЬТАТ",
                callback_data=f"check_result:{user_id}"
            )]
        ]
    )

# Кнопка "ПОЛУЧИТЬ БОНУС" — deep link к владельцу с автотекстом
def get_bonus_kb() -> InlineKeyboardMarkup:
    text = "Привет, пишу по поводу бонуса"
    encoded_text = quote(text)
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(
                text="ПОЛУЧИТЬ БОНУС",
                url=f"https://t.me/davidavidavidavidavidavidavid?text={encoded_text}"
            )]
        ]
    )

# Обработка заявки на вступление
@router.chat_join_request()
async def handle_join_request(join_request: ChatJoinRequest, bot: Bot):
    user_id = join_request.from_user.id
    chat_id = join_request.chat.id

    # Одобряем заявку
    await bot.approve_chat_join_request(chat_id=chat_id, user_id=user_id)

    # Сохраняем пользователя
    approved_users.add(user_id)

    # Приветственное сообщение с кнопкой
    photo = FSInputFile("media/welcome.jpg")
    await bot.send_photo(
        chat_id=user_id,
        photo=photo,
        caption="Привет! Спасибо за подписку на мой канал!\n\nНажми кнопку ниже, чтобы узнать результат:",
        reply_markup=learn_more_kb(user_id)
    )

# Обработка callback-кнопки "УЗНАТЬ РЕЗУЛЬТАТ"
@router.callback_query(F.data.startswith("check_result:"))
async def handle_check_result(callback: CallbackQuery, bot: Bot):
    user_id = int(callback.data.split(":")[1])

    try:
        photo = FSInputFile("media/welcome2.jpg")
        await bot.send_photo(
            chat_id=callback.from_user.id,
            photo=photo,
            caption="У меня для тебя есть БОНУС, который...",
            reply_markup=get_bonus_kb()
        )

        await asyncio.sleep(60)
        await bot.send_message(callback.from_user.id, "🔕 Не отключай уведомления этого бота.")
    except Exception as e:
        print(f"Ошибка при отправке бонуса: {e}")

    await callback.answer()  # Закрывает "часики"

# Обработка команды /start
@router.message(F.text.startswith("/start"))
async def handle_start(message: Message, bot: Bot):
    args = message.text.split()

    if len(args) > 1:
        param = args[1]

        if param == "bonus":
            await message.answer("🎁 Вот твой бонус!")
        else:
            await message.answer("👋 Привет! Используй кнопку в канале для получения бонуса.")
    else:
        await message.answer("👋 Привет! Это бот приветствий. Подпишись на канал, чтобы продолжить.")
