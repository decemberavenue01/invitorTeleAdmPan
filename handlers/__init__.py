# handlers/__init__.py

# Просто подтягиваем ADMIN_IDS из config, чтобы нигде не дублировать
from config import ADMIN_IDS

__all__ = ["ADMIN_IDS"]
