from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
import config

def support_keyboard():
    keyboard = InlineKeyboardMarkup()
    keyboard.add(InlineKeyboardButton("✉️ Contact Admin", url=f"tg://user?id={config.ADMIN_ID}"))
    return keyboard

def force_join_keyboard(channels):
    keyboard = InlineKeyboardMarkup(row_width=1)
    for ch in channels:
        keyboard.add(InlineKeyboardButton(text=ch['name'], url=ch['link']))
    keyboard.add(InlineKeyboardButton("✅ Verify", callback_data="verify_join"))
    return keyboard

def country_list_keyboard(countries):
    keyboard = InlineKeyboardMarkup(row_width=1)
    for name, qty, code in countries:
        btn_text = f"{name} ({qty})"
        keyboard.add(InlineKeyboardButton(text=btn_text, callback_data=f"buy_{code}"))
    keyboard.add(InlineKeyboardButton("🔙 Back to Menu", callback_data="back_to_main"))
    return keyboard

def number_action_keyboard(order_id, country_code):
    """৩টা মেইন বাটন: View OTP, Change Number, Change Country"""
    keyboard = InlineKeyboardMarkup(row_width=2)
    btn_view_otp = InlineKeyboardButton("📥 View OTP", callback_data=f"view_otp_{order_id}")
    btn_change_number = InlineKeyboardButton("🔄 Change Number", callback_data=f"change_{order_id}_{country_code}")
    btn_change_country = InlineKeyboardButton("🌍 Change Country", callback_data=f"cancel_{order_id}")
    
    keyboard.add(btn_view_otp)
    keyboard.add(btn_change_number, btn_change_country)
    return keyboard

def otp_success_keyboard():
    """ভিডিওর মত OTP গ্রুপের নিচের দুইটা বাটন"""
    keyboard = InlineKeyboardMarkup(row_width=2)
    keyboard.add(
        InlineKeyboardButton("🚀 Panel", url="https://t.me/your_panel_link"), 
        InlineKeyboardButton("🛒 Buy IP", url=f"tg://user?id={config.ADMIN_ID}")
    )
    return keyboard

def admin_main_keyboard():
    keyboard = InlineKeyboardMarkup(row_width=2)
    keyboard.add(
        InlineKeyboardButton("➕ Add Channel", callback_data="admin_add_ch"),
        InlineKeyboardButton("➖ Remove Channel", callback_data="admin_rm_ch")
    )
    keyboard.add(
        InlineKeyboardButton("➕ Add OTP Group", callback_data="admin_add_otp"),
        InlineKeyboardButton("➖ Remove OTP Group", callback_data="admin_rm_otp")
    )
    keyboard.add(InlineKeyboardButton("📢 Broadcast Message", callback_data="admin_broadcast"))
    return keyboard