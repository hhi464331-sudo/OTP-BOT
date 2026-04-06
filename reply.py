from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

def main_menu():
    """ইউজারের মেইন মেনু (100% Real)"""
    keyboard = ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
    keyboard.add(KeyboardButton("📱 Get Number"), KeyboardButton("🌍 Available Country"))
    keyboard.add(KeyboardButton("☎️ Support"))
    return keyboard