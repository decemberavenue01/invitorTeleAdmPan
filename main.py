import asyncio
import logging
from aiohttp import web

from aiogram import Bot, Dispatcher
from aiogram.enums import ParseMode
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.client.default import DefaultBotProperties

from config import (
    BOT_TOKEN, WEBHOOK_SECRET, WEBHOOK_PATH,
    BASE_WEBHOOK_URL, WEBHOOK_URL
)
from handlers import join_handler, broadcast_handler

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Создаём бота и диспетчер
bot = Bot(token=BOT_TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
dp = Dispatcher(storage=MemoryStorage())
dp.include_router(join_handler.router)
dp.include_router(broadcast_handler.router)

# Запуск webhook
async def on_startup(app):
    if not BASE_WEBHOOK_URL:
        logger.error("BASE_WEBHOOK_URL не задан. Webhook не будет установлен.")
        return
    await bot.set_webhook(WEBHOOK_URL, secret_token=WEBHOOK_SECRET)
    logger.info(f"Webhook установлен: {WEBHOOK_URL}")

# Удаление webhook при выключении
async def on_shutdown(app):
    await bot.delete_webhook()
    logger.info("Webhook удалён")

# Обработка входящих апдейтов
async def handler(request):
    if request.headers.get("X-Telegram-Bot-Api-Secret-Token") != WEBHOOK_SECRET:
        return web.Response(status=403)
    update = await request.json()
    await dp.feed_raw_update(bot=bot, update=update)
    return web.Response()

# Создание aiohttp-приложения
def create_app():
    app = web.Application()
    app.router.add_post(WEBHOOK_PATH, handler)
    app.on_startup.append(on_startup)
    app.on_shutdown.append(on_shutdown)
    return app

# Точка входа
if __name__ == "__main__":
    web.run_app(create_app(), port=8000)
