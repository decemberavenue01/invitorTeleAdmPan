# main.py

import asyncio
from aiogram import Bot, Dispatcher
from dotenv import load_dotenv

from config import BOT_TOKEN
from storage import init_db

# Загрузим .env
load_dotenv()

# Инициализация бота и диспетчера
bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

# Импорт и регистрация хэндлеров
from handlers.join_handler import register_join_handlers
from handlers.admin_handler import register_admin_handlers

# Теперь register_* сами ожидают Bot, Dispatcher
register_join_handlers(dp)
register_admin_handlers(dp, bot)

# Инициализируем БД перед запуском
async def on_startup():
    await init_db()

if __name__ == "__main__":
    dp.run_polling(bot, skip_updates=True, on_startup=on_startup)
