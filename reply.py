from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
import config

def main_menu(user_id, dynamic_menu_buttons=None):
    """
    ইউজারের মেইন মেনু। অ্যাডমিন প্যানেল থেকে সেট করা ডাইনামিক বাটন অটো অ্যাড হবে।
    """
    keyboard = ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
    keyboard.add(KeyboardButton("📱 Get Number"), KeyboardButton("🌍 Available Country"))
    
    # ডাইনামিক বাটনগুলো এখানে যুক্ত হবে (যদি অ্যাডমিন দিয়ে থাকে)
    if dynamic_menu_buttons:
        for btn in dynamic_menu_buttons:
            keyboard.add(KeyboardButton(text=btn['name'])) # Reply keyboard doesn't take URLs directly, usually acts as text command

    keyboard.add(KeyboardButton("☎️ Support"))
    
    if user_id == config.ADMIN_ID:
        keyboard.add(KeyboardButton("⚙️ Admin Panel"))
        
    return keyboard