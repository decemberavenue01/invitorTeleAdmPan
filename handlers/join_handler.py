from aiogram import Router, F, Bot
from aiogram.types import (
    ChatJoinRequest, Message, InlineKeyboardMarkup, InlineKeyboardButton
)
from aiogram.types.input_file import FSInputFile
from urllib.parse import quote
import asyncio
from data import approved_users
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

router = Router()

# Имя бота и владельца
BOT_USERNAME = "invitorTeleAdmPan_bot"          # Без @
OWNER_USERNAME = "davidavidavidavidavidavidavid"             # 🔁 ЗАМЕНИ на свой Telegram username без @

# Ссылка с параметром user_id
def get_deep_link(user_id: int) -> str:
    return f"https://t.me/{BOT_USERNAME}?start={user_id}"

# Кнопка "УЗНАТЬ РЕЗУЛЬТАТ" (ведёт к /start с параметром user_id)
def learn_more_kb(user_id: int) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(
                text="УЗНАТЬ РЕЗУЛЬТАТ",
                url=get_deep_link(user_id)
            )]
        ]
    )

# Генерация кнопки "ПОЛУЧИТЬ БОНУС" со ссылкой в личку к владельцу и автотекстом
def bonus_kb_with_prefill():
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

# Обработка старта с параметром
@router.message(F.text.startswith("/start"))
async def handle_start(message: Message, bot: Bot):
    args = message.text.split()

    if len(args) > 1:
        param = args[1]

        if param == "bonus":
            await message.answer("🎁 Вот твой бонус!")
        else:
            try:
                photo = FSInputFile("media/welcome2.jpg")
                await bot.send_photo(
                    chat_id=message.chat.id,
                    photo=photo,
                    caption="У меня для тебя есть БОНУС, который...",
                    reply_markup=bonus_kb_with_prefill()
                )

                await asyncio.sleep(30)
                await bot.send_message(message.chat.id, "🔕 Не отключай уведомления этого бота.")
            except Exception as e:
                print(f"Ошибка при отправке бонуса: {e}")
    else:
        await message.answer("👋 Привет! Это бот приветствий. Подпишись на канал, чтобы продолжить.")
