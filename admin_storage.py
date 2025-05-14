import json
from pathlib import Path

ADMINS_FILE = Path("admins.json")

def load_admins():
    if not ADMINS_FILE.exists():
        return []
    with open(ADMINS_FILE, "r", encoding="utf-8") as f:
        return json.load(f)

def save_admins(admins):
    with open(ADMINS_FILE, "w", encoding="utf-8") as f:
        json.dump(admins, f)

def add_admin(user_id):
    admins = load_admins()
    if user_id not in admins:
        admins.append(user_id)
        save_admins(admins)

def is_admin(user_id):
    return user_id in load_admins()