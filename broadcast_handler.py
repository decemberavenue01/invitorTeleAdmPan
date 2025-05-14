from aiogram import Router, F, types
from aiogram.filters import Command
from aiogram.types import (
    Message, InlineKeyboardButton, InlineKeyboardMarkup,
    ReplyKeyboardMarkup, KeyboardButton
)
from aiogram.fsm.context import FSMContext
from fsm.broadcast import BroadcastStates
from admin_storage import is_admin
from pathlib import Path
import json
import logging

# Инициализация логгера
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

router = Router()

@router.message(Command("broadcast"))
async def cmd_broadcast(message: Message, state: FSMContext):
    logger.info(f"User {message.from_user.id} sent /broadcast command.")
    if not is_admin(message.from_user.id):
        await message.answer("❌ У вас нет доступа к этой команде.")
        logger.info(f"User {message.from_user.id} attempted to access /broadcast without admin rights.")
        return

    await state.set_state(BroadcastStates.waiting_text)
    logger.info(f"State set to {BroadcastStates.waiting_text} for user {message.from_user.id}.")
    await message.answer(
        "Начинаем создание рассылки для пользователей.\n\n"
        "Пожалуйста, отправьте текст рассылки.\n"
        "Вы можете использовать HTML форматирование.\n\n"
        "Для отмены отправьте /cancel"
    )
    logger.info(f"User {message.from_user.id} started a broadcast.")

@router.message(Command("cancel"))
async def cancel(message: Message, state: FSMContext):
    await state.clear()
    await message.answer("Операция отменена.")
    logger.info(f"User {message.from_user.id} canceled the broadcast process.")

@router.message(BroadcastStates.waiting_text)
async def handle_text(message: Message, state: FSMContext):
    logger.info(f"User {message.from_user.id} entered waiting_text state and sent message: {message.text}")
    await state.update_data(text=message.text)

    markup = ReplyKeyboardMarkup(
        keyboard=[[KeyboardButton(text="Да")], [KeyboardButton(text="Нет")]],
        resize_keyboard=True
    )
    await state.set_state(BroadcastStates.waiting_photo_decision)
    await message.answer("Хотите добавить фотографию?", reply_markup=markup)
    logger.info(f"User {message.from_user.id} provided text for broadcast.")

@router.message(BroadcastStates.waiting_photo_decision, F.text.casefold() == "да")
async def photo_yes(message: Message, state: FSMContext):
    await state.set_state(BroadcastStates.waiting_photo)
    await message.answer("Пожалуйста, отправьте фотографию.", reply_markup=types.ReplyKeyboardRemove())
    logger.info(f"User {message.from_user.id} wants to add a photo to the broadcast.")

@router.message(BroadcastStates.waiting_photo_decision, F.text.casefold() == "нет")
async def photo_no(message: Message, state: FSMContext):
    await state.update_data(photo=None)
    await ask_button_decision(message, state)
    logger.info(f"User {message.from_user.id} does not want to add a photo to the broadcast.")

@router.message(BroadcastStates.waiting_photo, F.photo)
async def receive_photo(message: Message, state: FSMContext):
    await state.update_data(photo=message.photo[-1].file_id)
    await ask_button_decision(message, state)
    logger.info(f"User {message.from_user.id} provided a photo for the broadcast.")

async def ask_button_decision(message: Message, state: FSMContext):
    markup = ReplyKeyboardMarkup(
        keyboard=[[KeyboardButton(text="Да")], [KeyboardButton(text="Нет")]],
        resize_keyboard=True
    )
    await state.set_state(BroadcastStates.waiting_button_decision)
    await message.answer("Хотите добавить кнопку?", reply_markup=markup)
    logger.info(f"User {message.from_user.id} is deciding whether to add a button.")

@router.message(BroadcastStates.waiting_button_decision, F.text.casefold() == "да")
async def button_yes(message: Message, state: FSMContext):
    await state.set_state(BroadcastStates.waiting_button_url)
    await message.answer("Отправьте ссылку для кнопки.", reply_markup=types.ReplyKeyboardRemove())
    logger.info(f"User {message.from_user.id} wants to add a button to the broadcast.")

@router.message(BroadcastStates.waiting_button_decision, F.text.casefold() == "нет")
async def button_no(message: Message, state: FSMContext):
    await state.update_data(button_url=None, button_text=None)
    await confirm_broadcast(message, state)
    logger.info(f"User {message.from_user.id} does not want to add a button to the broadcast.")

@router.message(BroadcastStates.waiting_button_url)
async def button_url(message: Message, state: FSMContext):
    await state.update_data(button_url=message.text)
    await state.set_state(BroadcastStates.waiting_button_text)
    await message.answer("Введите текст кнопки.")
    logger.info(f"User {message.from_user.id} provided the URL for the button.")

@router.message(BroadcastStates.waiting_button_text)
async def button_text(message: Message, state: FSMContext):
    await state.update_data(button_text=message.text)
    await confirm_broadcast(message, state)
    logger.info(f"User {message.from_user.id} provided the text for the button.")

async def confirm_broadcast(message: Message, state: FSMContext):
    data = await state.get_data()
    text = data.get("text")
    photo = data.get("photo")
    button_url = data.get("button_url")
    button_text = data.get("button_text")

    markup = None
    if button_url and button_text:
        markup = InlineKeyboardMarkup(
            inline_keyboard=[[InlineKeyboardButton(text=button_text, url=button_url)]]
        )
        await state.update_data(markup=markup)
        logger.info(f"User {message.from_user.id} added a button to the broadcast.")

    await state.set_state(BroadcastStates.waiting_confirmation)

    # Превью рассылки
    if photo:
        await message.bot.send_photo(
            chat_id=message.chat.id,
            photo=photo,
            caption=text,
            reply_markup=markup
        )
    else:
        await message.bot.send_message(
            chat_id=message.chat.id,
            text=text,
            reply_markup=markup
        )

    await message.answer("Подтверждаете рассылку? (Да/Нет)")
    logger.info(f"User {message.from_user.id} is confirming the broadcast.")

@router.message(BroadcastStates.waiting_confirmation, F.text.casefold() == "да")
async def confirm_send(message: Message, state: FSMContext):
    data = await state.get_data()
    USERS_FILE = Path("users.json")

    if USERS_FILE.exists():
        with open(USERS_FILE, "r", encoding="utf-8") as f:
            users = json.load(f)
        logger.info(f"Loaded {len(users)} users for broadcast.")
    else:
        users = []
        logger.warning("No users found for broadcast.")

    markup = data.get("markup")
    for user_id in users:
        try:
            if data.get("photo"):
                await message.bot.send_photo(user_id, data["photo"], caption=data["text"], reply_markup=markup)
                logger.info(f"Sent broadcast photo to user {user_id}")
            else:
                await message.bot.send_message(user_id, data["text"], reply_markup=markup)
                logger.info(f"Sent broadcast message to user {user_id}")
        except Exception as e:
            logger.error(f"Failed to send message to user {user_id}: {e}")
            continue

    await state.clear()
    await message.answer("✅ Рассылка завершена.")
    logger.info("Broadcast completed successfully.")

@router.message(BroadcastStates.waiting_confirmation, F.text.casefold() == "нет")
async def cancel_broadcast(message: Message, state: FSMContext):
    await state.clear()
    await message.answer("❌ Рассылка отменена.")
    logger.info(f"User {message.from_user.id} canceled the broadcast confirmation.")
