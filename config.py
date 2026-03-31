import os
from dotenv import load_dotenv

load_dotenv()

# Telegram
BOT_TOKEN = os.getenv("BOT_TOKEN", "your_bot_token")
ADMIN_ID = int(os.getenv("ADMIN_ID", "your_admin_id"))

# MongoDB
MONGO_URI = os.getenv("MONGO_URI", "your_mongodb_uri")

# API (5sim / SMS-Activate) - রিয়েল কাজের জন্য
API_KEY = os.getenv("API_KEY", "your_api_key")
API_URL = "https://5sim.net/v1/guest" # আপনার API অনুযায়ী চেঞ্জ করবেন