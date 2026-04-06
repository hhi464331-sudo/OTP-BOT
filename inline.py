from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
import config

def support_keyboard():
    return InlineKeyboardMarkup().add(InlineKeyboardButton("✉️ Contact Admin", url=f"tg://user?id={config.ADMIN_ID}"))

def force_join_keyboard(channels, groups):
    """Force Join এর চ্যানেল ও গ্রুপ লিস্ট দেখাবে"""
    keyboard = InlineKeyboardMarkup(row_width=1)
    for idx, ch in enumerate(channels, 1):
        keyboard.add(InlineKeyboardButton(text=f"📢 Join Channel {idx}", url=ch.get('link', 'https://t.me')))
    for idx, grp in enumerate(groups, 1):
        keyboard.add(InlineKeyboardButton(text=f"👥 Join Group {idx}", url=grp.get('link', 'https://t.me')))
    keyboard.add(InlineKeyboardButton("✅ Verify", callback_data="verify_join"))
    return keyboard

def country_list_keyboard(countries):
    keyboard = InlineKeyboardMarkup(row_width=1)
    for name, qty, code in countries:
        keyboard.add(InlineKeyboardButton(text=f"{name} ({qty})", callback_data=f"buy_{code}"))
    keyboard.add(InlineKeyboardButton("🔙 Back to Menu", callback_data="back_to_main"))
    return keyboard

def number_action_keyboard(order_id, country_code):
    keyboard = InlineKeyboardMarkup(row_width=2)
    keyboard.add(InlineKeyboardButton("📥 View OTP 📩", callback_data=f"view_otp_list_{order_id}"))
    keyboard.add(InlineKeyboardButton("🔄 Change Number", callback_data=f"change_{order_id}_{country_code}"),
                 InlineKeyboardButton("🌍 Change Country", callback_data=f"cancel_{order_id}"))
    return keyboard

def view_otp_sources_keyboard(otp_channels, otp_groups):
    """View OTP তে চাপ দিলে এই লিস্ট দেখাবে"""
    keyboard = InlineKeyboardMarkup(row_width=1)
    for idx, ch in enumerate(otp_channels, 1):
        keyboard.add(InlineKeyboardButton(text=f"📢 OTP Channel {idx}", url=ch.get('link', 'https://t.me')))
    for idx, grp in enumerate(otp_groups, 1):
        keyboard.add(InlineKeyboardButton(text=f"👥 OTP Group {idx}", url=grp.get('link', 'https://t.me')))
    keyboard.add(InlineKeyboardButton("🔙 Back", callback_data="back_to_main"))
    return keyboard

def otp_success_keyboard():
    keyboard = InlineKeyboardMarkup(row_width=2)
    keyboard.add(InlineKeyboardButton("🚀 Panel", url="https://t.me/your_panel"), 
                 InlineKeyboardButton("🛒 Buy IP", url=f"tg://user?id={config.ADMIN_ID}"))
    return keyboard

def admin_main_keyboard(is_online=True):
    """আপনার দেওয়া UI Structure অনুযায়ী প্যানেল"""
    keyboard = InlineKeyboardMarkup(row_width=2)
    
    # Force Join Section
    keyboard.add(InlineKeyboardButton("📢 Add FJ Channel", callback_data="add_fj_ch"),
                 InlineKeyboardButton("👥 Add FJ Group", callback_data="add_fj_gr"))
    keyboard.add(InlineKeyboardButton("➖ Remove FJ Channel", callback_data="rm_fj_ch"),
                 InlineKeyboardButton("➖ Remove FJ Group", callback_data="rm_fj_gr"))
    
    # OTP Section
    keyboard.add(InlineKeyboardButton("📨 Add OTP Channel", callback_data="add_otp_ch"),
                 InlineKeyboardButton("📨 Add OTP Group", callback_data="add_otp_gr"))
    keyboard.add(InlineKeyboardButton("➖ Remove OTP Channel", callback_data="rm_otp_ch"),
                 InlineKeyboardButton("➖ Remove OTP Group", callback_data="rm_otp_gr"))
    
    # Broadcast & System
    keyboard.add(InlineKeyboardButton("📢 Broadcast Message", callback_data="admin_broadcast"))
    keyboard.add(InlineKeyboardButton("📊 Active Users", callback_data="admin_stats"),
                 InlineKeyboardButton("📁 Member List", callback_data="admin_members"))
    
    power_text = "🟢 System: ON" if is_online else "🔴 System: OFF"
    keyboard.add(InlineKeyboardButton(power_text, callback_data="admin_power_toggle"))
    return keyboard