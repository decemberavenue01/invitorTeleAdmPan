# config.py

import os
from dotenv import load_dotenv

load_dotenv()  # подгрузит .env из корня проекта

# Токен бота
BOT_TOKEN = os.getenv("BOT_TOKEN")

# Список админов (Telegram ID) — через запятую в .env
_ADMIN_IDS = os.getenv("ADMIN_IDS", "")
ADMIN_IDS = set(int(x) for x in _ADMIN_IDS.split(",") if x)

# Канал, в котором бот админит (не используется в обработках сейчас,
# но может понадобиться, например, для approve_chat_join_request)
CHANNEL_ID = os.getenv("CHANNEL_ID")
