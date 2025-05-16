from aiogram import Router, F, Bot
from aiogram.types import (
    ChatJoinRequest, Message, InputMediaPhoto,
    InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery
)
from aiogram.types.input_file import FSInputFile
from urllib.parse import quote
import asyncio
from aiogram.enums import ParseMode
import json
import os
from aiogram.filters import CommandStart


router = Router()

BOT_USERNAME = "invitorTeleAdmPan_bot"           # без @
OWNER_USERNAME = "ray_trdr" # без @
USERS_FILE = "users.json"

def save_user(user_id):
    if not os.path.exists(USERS_FILE):
        with open(USERS_FILE, 'w', encoding='utf-8') as f:
            json.dump([], f)

    with open(USERS_FILE, 'r', encoding='utf-8') as f:
        try:
            users = json.load(f)
        except json.JSONDecodeError:
            users = []

    if user_id not in users:
        users.append(user_id)
        with open(USERS_FILE, 'w', encoding='utf-8') as f:
            json.dump(users, f)

def learn_more_kb(user_id: int) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(
                text="Узнать результаты💸",
                callback_data=f"check_result:{user_id}"
            )]
        ]
    )

def get_bonus_kb() -> InlineKeyboardMarkup:
    text = "Активировать протокол"
    encoded_text = quote(text)
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(
                text="Активировать протокол💬",
                url=f"https://t.me/{OWNER_USERNAME}?text={encoded_text}"
            )]
        ]
    )

async def send_intro_with_media(user_id: int, bot: Bot):
    media_files = [
        "media/welcome2.jpg",
        "media/welcome3.jpg",
        "media/welcome4.jpg",
        "media/welcome5.jpg",
        "media/welcome6.jpg"
    ]

    try:
        media_group = [InputMediaPhoto(media=FSInputFile(file)) for file in media_files]
        await bot.send_media_group(chat_id=user_id, media=media_group)

        await bot.send_message(
            chat_id=user_id,
            text=(
                "🤝🏻<b>Благодаря моему каналу ты сможешь подружиться с ВАЛЮТНЫМ РЫНКОМ💹</b>\n\n"
                "<blockquote><b>Мы торгуем с понедельника по пятницу и я регулярно выкладываю отчёты!</b></blockquote>\n\n"
                "Мой <b>бесплатный</b> канал с сигналами и обучающим материалами называется:\n"
                "<tg-spoiler><b>The R.A.Y. Protocol</b></tg-spoiler>\n\n"
                "<i>Напиши мне</i>\n"
                "<b>« Активировать протокол »</b>, и я дам пошаговую инструкцию!😉\n\n"
                "❕ВАЖНЫЙ МОМЕНТ❕\n\n"
                "У меня есть <b>БОНУС</b>, который поможет быстро стартануть и увидеть <b>результаты!</b>💰💰💰"
            ),
            reply_markup=get_bonus_kb(),
            parse_mode=ParseMode.HTML
        )

        await asyncio.sleep(20)

        await bot.send_message(
            chat_id=user_id,
            text=(
                "⚡️<b>Важно</b>⚡️\n\n"
                "🔕<b>Не отключай уведомления этого бота.</b>\n"
                "Он будет присылать только полезную информацию.\n\n"
                "Уже скоро что-то отправлю!"
            ),
            parse_mode=ParseMode.HTML
        )

    except Exception as e:
        print(f"Ошибка при отправке бонуса: {e}")

@router.chat_join_request()
async def handle_join_request(join_request: ChatJoinRequest, bot: Bot):
    user_id = join_request.from_user.id
    chat_id = join_request.chat.id

    await bot.approve_chat_join_request(chat_id=chat_id, user_id=user_id)

    start_link = f"https://t.me/{BOT_USERNAME}?start={user_id}"

    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="Узнать результаты💸", url=start_link)]
    ])

    photo = FSInputFile("media/welcome.jpg")

    await bot.send_photo(
        chat_id=user_id,
        photo=photo,
        caption=(
            "👋🏻<b>Привет! спасибо за подписку на мой канал!</b>\n\n"
    "У меня нет никаких:\n"
    "<blockquote>❌<b>VIP каналов.\n"
    "❌Платных курсов.\n"
    "❌Доверительного управления.</b></blockquote>\n\n"
    "Моя цель набрать <b>100k подписчиков!</b>\n"
    "Я торгую по собственной стратегии с <b>Winrate 90%!</b> тем самым приумножаю свой капитал и помогаю в этом своим подписчикам!\n\n"
    "⚠️<b>Как именно я помогаю:</b>\n"
    "<blockquote>🔸<b>Бесплатно провожу торговые сессии, чтоб вы могли зарабатывать вместе со мной</b>\n"
    "🔸<b>Даю полезный материал для трейдеров и различные торговые стратегии</b></blockquote>\n\n"
    "Нажми кнопку ниже и узнаешь какие результаты ты сможешь делать с <b>первого дня</b>👇🏻"
        ),
        reply_markup=keyboard,
        parse_mode=ParseMode.HTML
    )

@router.message(CommandStart(deep_link=True))
async def start_handler(message: Message, bot: Bot):
    user_id = message.from_user.id
    save_user(user_id)

    args = message.text.split(maxsplit=1)[1] if len(message.text.split()) > 1 else ""
    print(f"/start вызван с args={args}")

    await send_intro_with_media(user_id, bot)

@router.callback_query(F.data.startswith("check_result:"))
async def handle_check_result(callback: CallbackQuery, bot: Bot):
    await send_intro_with_media(callback.from_user.id, bot)
    await callback.answer()
