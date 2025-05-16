from aiogram import Router, F
from aiogram.types import Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import InputMediaPhoto
from config import ADMIN_IDS

import json
import os
from datetime import datetime, timedelta
import asyncio

router = Router()

USERS_FILE = "users.json"

class BroadcastState(StatesGroup):
    waiting_for_text = State()
    waiting_for_media_choice = State()
    waiting_for_photo = State()
    waiting_for_video_note = State()
    waiting_for_button_text = State()
    waiting_for_button_url = State()
    confirming = State()
    waiting_for_delay_minutes = State()

def get_all_users():
    if not os.path.exists(USERS_FILE):
        return []
    with open(USERS_FILE, 'r', encoding='utf-8') as f:
        return json.load(f)

@router.message(F.text == "/broadcast")
async def start_broadcast(msg: Message, state: FSMContext):
    if msg.from_user.id not in ADMIN_IDS:
        await msg.answer("У вас нет прав для этой команды.")
        return
    await state.clear()
    await msg.answer("<b>Начинаем создание рассылки.</b>\n\nПожалуйста, отправьте текст рассылки.\n<b>Отправьте /cancel для отмены в любой момент.</b>")
    await state.set_state(BroadcastState.waiting_for_text)

@router.message(F.text == "/cancel")
async def cancel_broadcast(msg: Message, state: FSMContext):
    await state.clear()
    await msg.answer("<b>Рассылка отменена.</b>")

@router.message(F.text == "/help")
async def admin_help(msg: Message):
    if msg.from_user.id not in ADMIN_IDS:
        return
    await msg.answer("Доступные команды:\n\n/broadcast - создать автоматическую рассылку пользователям.\n/help - показать это сообщение.")

@router.message(BroadcastState.waiting_for_text)
async def get_text(msg: Message, state: FSMContext):
    if msg.text == "/cancel":
        await cancel_broadcast(msg, state)
        return
    await state.update_data(text=msg.text)
    await msg.answer("<b>Хотите прикрепить изображение или «кружок»?</b>", reply_markup=InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="Фото", callback_data="photo"),
         InlineKeyboardButton(text="Кружок", callback_data="video_note")],
        [InlineKeyboardButton(text="Нет", callback_data="no_media")]
    ]))
    await state.set_state(BroadcastState.waiting_for_media_choice)

@router.callback_query(BroadcastState.waiting_for_media_choice)
async def media_choice(call: CallbackQuery, state: FSMContext):
    await call.answer()
    if call.data == "photo":
        await call.message.answer("<b>Отправьте фото.</b>")
        await state.set_state(BroadcastState.waiting_for_photo)
    elif call.data == "video_note":
        await call.message.answer("<b>Отправьте кружок (видео note).</b>")
        await state.set_state(BroadcastState.waiting_for_video_note)
    elif call.data == "no_media":
        await ask_for_button(call.message, state)
        await state.set_state(BroadcastState.confirming)  # Перейти к следующему шагу

@router.message(BroadcastState.waiting_for_photo, F.photo)
async def get_photo(msg: Message, state: FSMContext):
    await state.update_data(photo=msg.photo[-1].file_id)
    await ask_for_button(msg, state)
    await state.set_state(BroadcastState.confirming)

@router.message(BroadcastState.waiting_for_video_note, F.video_note)
async def get_video_note(msg: Message, state: FSMContext):
    await state.update_data(video_note=msg.video_note.file_id)
    await ask_for_button(msg, state)
    await state.set_state(BroadcastState.confirming)

async def ask_for_button(msg: Message, state: FSMContext):
    await msg.answer("<b>Хотите добавить кнопку со ссылкой?</b>", reply_markup=InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="Да", callback_data="yes_button"),
         InlineKeyboardButton(text="Нет", callback_data="no_button")]
    ]))

@router.callback_query(F.data == "yes_button")
async def button_yes(call: CallbackQuery, state: FSMContext):
    await call.answer()
    await call.message.answer("<b>Введите текст для кнопки:</b>")
    await state.set_state(BroadcastState.waiting_for_button_text)

@router.callback_query(F.data == "no_button")
async def button_no(call: CallbackQuery, state: FSMContext):
    await call.answer()
    await show_preview(call.message, state)
    await state.set_state(BroadcastState.confirming)

@router.message(BroadcastState.waiting_for_button_text)
async def button_text(msg: Message, state: FSMContext):
    if msg.text == "/cancel":
        await cancel_broadcast(msg, state)
        return
    await state.update_data(button_text=msg.text)
    await msg.answer("<b>Теперь введите ссылку.</b>\n\n"
                     "Поддерживаются ссылки на каналы/сайты/чаты.\n"
                     "Также ссылки формата: www.domain, для перехода в личные сообщения - t.me/юзернейм ( БЕЗ @).")
    await state.set_state(BroadcastState.waiting_for_button_url)

@router.message(BroadcastState.waiting_for_button_url)
async def button_url(msg: Message, state: FSMContext):
    if msg.text == "/cancel":
        await cancel_broadcast(msg, state)
        return
    await state.update_data(button_url=msg.text)
    await show_preview(msg, state)
    await state.set_state(BroadcastState.confirming)

async def show_preview(msg: Message, state: FSMContext):
    data = await state.get_data()
    keyboard = None
    if 'button_text' in data and 'button_url' in data:
        keyboard = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text=data['button_text'], url=data['button_url'])]
        ])
    await msg.answer("\U0001F4E2 Предпросмотр рассылки:")
    if 'photo' in data:
        await msg.answer_photo(photo=data['photo'], caption=data['text'], reply_markup=keyboard)
    elif 'video_note' in data:
        await msg.answer_video_note(video_note=data['video_note'], reply_markup=keyboard)
    else:
        await msg.answer(data['text'], reply_markup=keyboard)

    await msg.answer("<b>Отправить рассылку сейчас или через определённое количество минут?</b>", reply_markup=InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="Сейчас", callback_data="confirm_send")],
        [InlineKeyboardButton(text="Отложить", callback_data="delay_send")],
        [InlineKeyboardButton(text="❌ Отмена", callback_data="cancel_send")]
    ]))

@router.callback_query(BroadcastState.confirming)
async def confirm_broadcast(call: CallbackQuery, state: FSMContext):
    await call.answer()
    if call.data == "cancel_send":
        await state.clear()
        await call.message.edit_text("<b>Рассылка отменена.</b>")
        return
    if call.data == "delay_send":
        await call.message.answer("<b>Через сколько минут отправить рассылку?</b>")
        await state.set_state(BroadcastState.waiting_for_delay_minutes)
        return
    await perform_broadcast(call.message, state)

@router.message(BroadcastState.waiting_for_delay_minutes)
async def delay_minutes(msg: Message, state: FSMContext):
    if msg.text == "/cancel":
        await cancel_broadcast(msg, state)
        return
    try:
        delay = int(msg.text)
        await msg.answer(f"Рассылка будет отправлена через {delay} минут.")
        await asyncio.sleep(delay * 60)
        await perform_broadcast(msg, state)
    except ValueError:
        await msg.answer("Пожалуйста, введите число — количество минут.")

async def perform_broadcast(msg_or_call, state: FSMContext):
    data = await state.get_data()
    users = get_all_users()
    keyboard = None
    if 'button_text' in data and 'button_url' in data:
        keyboard = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text=data['button_text'], url=data['button_url'])]
        ])

    count = 0
    for user_id in users:
        try:
            if 'photo' in data:
                await msg_or_call.bot.send_photo(
                    chat_id=user_id,
                    photo=data['photo'],
                    caption=data['text'],
                    reply_markup=keyboard,
                    parse_mode="HTML"
                )
            elif 'video_note' in data:
                await msg_or_call.bot.send_video_note(
                    chat_id=user_id,
                    video_note=data['video_note'],
                    reply_markup=keyboard
                )
            else:
                await msg_or_call.bot.send_message(
                    chat_id=user_id,
                    text=data['text'],
                    reply_markup=keyboard,
                    parse_mode="HTML"
                )
            count += 1
        except Exception as e:
            print(f"Ошибка при отправке {user_id}: {e}")

    await msg_or_call.answer(f"Рассылка завершена. Успешно отправлено: {count}")
    await state.clear()
