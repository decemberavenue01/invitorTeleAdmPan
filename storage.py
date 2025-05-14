# storage.py

import os
import json
from typing import List

# Путь к файлу data/db.json
DB_FILE = os.path.join(os.path.dirname(__file__), 'data', 'db.json')

async def init_db():
    """
    Инициализация файла db.json, если он не существует.
    """
    if not os.path.exists(DB_FILE):
        os.makedirs(os.path.dirname(DB_FILE), exist_ok=True)
        with open(DB_FILE, 'w', encoding='utf-8') as f:
            json.dump({"users": []}, f, ensure_ascii=False, indent=4)

async def add_user_to_db(user_id: int):
    """
    Добавляет user_id в список users в db.json (если ещё нет).
    """
    # читаем текущее содержимое
    if os.path.exists(DB_FILE):
        with open(DB_FILE, 'r', encoding='utf-8') as f:
            data = json.load(f)
    else:
        data = {"users": []}

    if user_id not in data.get("users", []):
        data["users"].append(user_id)
        with open(DB_FILE, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=4)

async def get_all_users() -> List[int]:
    """
    Возвращает список всех user_id из db.json.
    """
    if not os.path.exists(DB_FILE):
        return []
    with open(DB_FILE, 'r', encoding='utf-8') as f:
        data = json.load(f)
    return data.get("users", [])
