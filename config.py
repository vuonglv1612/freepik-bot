import os

BOT_TOKEN = os.getenv("BOT_TOKEN")
ALLOWED_CHATS = os.getenv("ALLOWED_CHATS", "").split(",")
REDIS_URI = os.getenv("REDIS_URI")
EMAIL = os.getenv("EMAIL")
PASSWORD = os.getenv("PASSWORD")
