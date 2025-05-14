import asyncio
import logging
import json
from pathlib import Path

from aiogram import Bot, Dispatcher, F
from aiogram.enums import ParseMode
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.fsm.strategy import FSMStrategy
from aiogram.types import Message
from aiogram.client.default import DefaultBotProperties

from config import BOT_TOKEN
from handlers import join_handler, admin_panel
from admin_storage import add_admin
from broadcast_handler import router as broadcast_router

# 📂 Файл для хранения ID пользователей
USERS_FILE = Path("users.json")

# 🔧 Настройка логирования
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# 🤖 Инициализация бота и диспетчера
bot = Bot(token=BOT_TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
dp = Dispatcher(storage=MemoryStorage(), fsm_strategy=FSMStrategy.CHAT)

# 📦 Регистрация роутеров
dp.include_router(join_handler.router)
dp.include_router(admin_panel.router)
dp.include_router(broadcast_router)

# ✅ Обработка кода администратора
@dp.message(F.text == "adminpanel2025invitor")
async def grant_admin(message: Message):
    add_admin(message.from_user.id)
    await message.answer("✅ Вы стали администратором бота.")

# 💾 Сохранение пользователя
def save_user(user_id: int):
    if USERS_FILE.exists():
        with open(USERS_FILE, "r", encoding="utf-8") as f:
            users = json.load(f)
    else:
        users = []

    if user_id not in users:
        users.append(user_id)
        with open(USERS_FILE, "w", encoding="utf-8") as f:
            json.dump(users, f)

# 📥 Отслеживание пользователей
@dp.message()
async def track_user(message: Message):
    save_user(message.from_user.id)

# 🚀 Запуск бота
async def main():
    logger.info("Бот запускается...")
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
