
import os
from dotenv import load_dotenv

load_dotenv()

# Токен бота
BOT_TOKEN = os.getenv("BOT_TOKEN")

# данные владельца из .env
OWNER_USERNAME = os.getenv("OWNER_USERNAME", "")
OWNER_ID = int(os.getenv("OWNER_ID", 0))


ADMIN_IDS = [
    int(uid) for uid in os.getenv("ADMIN_IDS", "").split(",")
    if uid.strip().isdigit()
]

# ID канала (если будет нужен)
CHANNEL_ID = int(os.getenv("CHANNEL_ID", 0))
