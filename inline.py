from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
import config

def support_keyboard():
    return InlineKeyboardMarkup().add(InlineKeyboardButton("✉️ Contact Admin", url=f"tg://user?id={config.ADMIN_ID}"))

def country_list_keyboard(countries):
    keyboard = InlineKeyboardMarkup(row_width=1)
    for name, qty, code in countries:
        keyboard.add(InlineKeyboardButton(text=f"{name} ({qty})", callback_data=f"buy_{code}"))
    keyboard.add(InlineKeyboardButton("🔙 Back to Menu", callback_data="back_to_main"))
    return keyboard

def number_action_keyboard(order_id, country_code):
    """নাম্বার নেওয়ার পর মেনু"""
    keyboard = InlineKeyboardMarkup(row_width=2)
    keyboard.add(InlineKeyboardButton("📥 View OTP 📩", callback_data=f"view_otp_list_{order_id}_{country_code}"))
    keyboard.add(InlineKeyboardButton("🔄 Change Number", callback_data=f"change_{order_id}_{country_code}"),
                 InlineKeyboardButton("🌍 Cancel", callback_data=f"cancel_{order_id}"))
    return keyboard

def view_otp_sources_keyboard(otp_sources, order_id, country_code):
    """
    ম্যাজিক লজিক: 
    ১টা থাকলে ডিরেক্ট পপ-আপ লিংক, বেশি থাকলে লিস্ট।
    আর Back বাটন দিলে আগের নাম্বারে ফেরত যাবে!
    """
    keyboard = InlineKeyboardMarkup(row_width=1)
    
    if len(otp_sources) == 1:
        # ১টা থাকলে ডিরেক্ট ইনভাইট লিংক পপ-আপ হবে
        keyboard.add(InlineKeyboardButton(text=f"🚀 Join & View OTP", url=otp_sources[0].get('link')))
    else:
        # একাধিক থাকলে সুন্দর করে নাম দেখাবে
        for src in otp_sources:
            keyboard.add(InlineKeyboardButton(text=f"👉 {src.get('name')}", url=src.get('link')))
            
    # গ্লিচ ফিক্সড: আগের জায়গায় ফেরত যাওয়ার লজিক
    keyboard.add(InlineKeyboardButton("🔙 Back", callback_data=f"back_to_order_{order_id}_{country_code}"))
    return keyboard

def otp_success_keyboard(dynamic_buttons=None):
    """OTP মেসেজের নিচে অ্যাডমিনের সেট করা ডায়নামিক বাটন বসবে"""
    keyboard = InlineKeyboardMarkup(row_width=1)
    if dynamic_buttons:
        for btn in dynamic_buttons:
            keyboard.add(InlineKeyboardButton(text=btn['name'], url=btn['link']))
    return keyboard

def admin_main_keyboard(is_online=True):
    keyboard = InlineKeyboardMarkup(row_width=2)
    
    keyboard.add(InlineKeyboardButton("📢 Add FJ Channel", callback_data="add_fj_ch"),
                 InlineKeyboardButton("👥 Add FJ Group", callback_data="add_fj_gr"))
    
    keyboard.add(InlineKeyboardButton("📨 Add OTP Channel", callback_data="add_otp_ch"),
                 InlineKeyboardButton("📨 Add OTP Group", callback_data="add_otp_gr"))
                 
    # New: Dynamic Button Manager
    keyboard.add(InlineKeyboardButton("🔘 Manage OTP Buttons", callback_data="manage_otp_btn"),
                 InlineKeyboardButton("🔘 Manage Menu Buttons", callback_data="manage_menu_btn"))
    
    keyboard.add(InlineKeyboardButton("📢 Broadcast", callback_data="admin_broadcast"),
                 InlineKeyboardButton("📊 Detailed Stats", callback_data="admin_stats"))
                 
    keyboard.add(InlineKeyboardButton("📁 Download Member List", callback_data="admin_members"))
    
    power_text = "🟢 System: ON" if is_online else "🔴 System: OFF"
    keyboard.add(InlineKeyboardButton(power_text, callback_data="admin_power_toggle"))
    return keyboard