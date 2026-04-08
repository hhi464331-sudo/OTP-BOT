from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
import config

def main_menu(user_id):
    """ইউজারের মেইন মেনু। অ্যাডমিন হলে এক্সট্রা বাটন দেখাবে।"""
    keyboard = ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
    keyboard.add(KeyboardButton("📱 Get Number"), KeyboardButton("🌍 Available Country"))
    keyboard.add(KeyboardButton("☎️ Support"))
    
    # যদি ইউজার অ্যাডমিন হয়, তাহলে ৪ নাম্বার বাটনটা আসবে
    if user_id == config.ADMIN_ID:
        keyboard.add(KeyboardButton("⚙️ Admin Panel"))
        
    return keyboard