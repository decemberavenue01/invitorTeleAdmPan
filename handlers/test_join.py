from aiogram import Router, F, Bot
from aiogram.types import (
    ChatJoinRequest, Message, InputMediaPhoto,
    InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery
)
from aiogram.types.input_file import FSInputFile
from urllib.parse import quote
import asyncio
from aiogram.enums import ParseMode


router = Router()

# Имя бота и владельца
BOT_USERNAME = "invitorTeleAdmPan_bot"         # Без @
OWNER_USERNAME = "davidavidavidavidavidavidavid"  # ✅ Твой username без @

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
                url=f"https://t.me/{OWNER_USERNAME}?text={encoded_text}"
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

    # Приветственное сообщение с кнопкой
    photo = FSInputFile("media/welcome.jpg")
    await bot.send_photo(
        chat_id=user_id,
        photo=photo,
        caption="👋🏻<b>Привет! спасибо за подписку на мой канал!</b>\n\n"
    "У меня нет никаких:\n"
    "<blockquote>❌<b>VIP каналов.\n"
    "❌Платных курсов.\n"
    "❌Доверительного управления.</b></blockquote>\n\n"
    "Моя цель набрать <b>100k подписчиков!</b>\n"
    "Я торгую по собственной стратегии с <b>Winrate 90%!</b> тем самым приумножаю свой капитал и помогаю в этом своим подписчикам!\n\n"
    "⚠️<b>Как именно я помогаю:</b>\n"
    "<blockquote>🔸<b>Бесплатно провожу торговые сессии, чтоб вы могли зарабатывать вместе со мной</b>\n"
    "🔸<b>Даю полезный материал для трейдеров и различные торговые стратегии</b></blockquote>\n\n"
    "Нажми кнопку ниже и узнаешь какие результаты ты сможешь делать с <b>первого дня</b>👇🏻",
        reply_markup=learn_more_kb(user_id)
    )

# Обработка callback-кнопки "УЗНАТЬ РЕЗУЛЬТАТ"
@router.callback_query(F.data.startswith("check_result:"))
async def handle_check_result(callback: CallbackQuery, bot: Bot):
    user_id = callback.from_user.id

    media_files = [
        "media/welcome2.jpg",
        "media/welcome3.jpg",
        "media/welcome4.jpg",
        "media/welcome5.jpg",
        "media/welcome6.jpg"
    ]

    try:
        media_group = [InputMediaPhoto(media=FSInputFile(file)) for file in media_files]

        # Отправляем медиагруппу
        await bot.send_media_group(chat_id=user_id, media=media_group)

        # Отправляем отдельное сообщение с кнопкой
        await bot.send_message(
            chat_id=user_id,
            text="🤝🏻<b>Благодаря моему каналу ты сможешь подружиться с ВАЛЮТНЫМ РЫНКОМ💹</b>\n\n"
                 "<blockquote><b>Мы торгуем с понедельника по пятницу и я регулярно выкладываю все отчёты!</b></blockquote>\n\n"
                 "Мой <b>бесплатный</b> канал с сигналами и обучающим материалами называется:\n"
                 "<tg-spoiler><b>The R.A.Y. Protocol</b></tg-spoiler>\n\n"
                 "Чтоб присоединиться, просто напиши мне <b>« Активировать протокол »</b> и я напишу тебе пошагавшую инструкцию с чего начать!😉\n\n"
                 "❕ВАЖНЫЙ МОМЕНТ❕\n\n"
                 "У меня для тебя есть БОНУС который поможет быстро стартануть уже сегодня и увидеть первые результаты!💰💰💰",
            reply_markup=get_bonus_kb()
        )

        await asyncio.sleep(15)
        await bot.send_message(user_id,
        "Важно!\n\n"
            "🔕<b>Не отключай уведомления этого бота.</b>\n"
            "Он не будет спамить ненужным, а будет отправлять тебе всё больше бесплатной и полезной информации.\n\n"
            "Уже скоро он отправит кое что полезное!")
    except Exception as e:
        print(f"Ошибка при отправке бонуса: {e}")

    await callback.answer()
