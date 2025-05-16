import os
from dotenv import load_dotenv

load_dotenv()

# Токен бота
BOT_TOKEN = os.getenv("BOT_TOKEN")

# Данные владельца
OWNER_USERNAME = os.getenv("OWNER_USERNAME", "")
OWNER_ID = int(os.getenv("OWNER_ID", 0))

# Список админов
ADMIN_IDS = [
    int(uid) for uid in os.getenv("ADMIN_IDS", "").split(",")
    if uid.strip().isdigit()
]

# ID канала (если нужно)
CHANNEL_ID = int(os.getenv("CHANNEL_ID", 0))

# Настройки Webhook
WEBHOOK_SECRET = os.getenv("WEBHOOK_SECRET", "supersecrettoken123")
WEBHOOK_PATH = f"/webhook/{WEBHOOK_SECRET}"

BASE_WEBHOOK_URL = os.getenv("BASE_WEBHOOK_URL", "")
WEBHOOK_URL = f"{BASE_WEBHOOK_URL}{WEBHOOK_PATH}" if BASE_WEBHOOK_URL else ""
