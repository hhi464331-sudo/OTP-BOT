from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
import config

def support_keyboard():
    """সরাসরি অ্যাডমিনের ইনবক্সে নেওয়ার বাটন"""
    keyboard = InlineKeyboardMarkup()
    keyboard.add(InlineKeyboardButton("✉️ Contact Admin", url=f"tg://user?id={config.ADMIN_ID}"))
    return keyboard

def force_join_keyboard(channels):
    """ডাটাবেস থেকে রিয়েল চ্যানেল এনে বাটন বানাবে"""
    keyboard = InlineKeyboardMarkup(row_width=1)
    for ch in channels:
        keyboard.add(InlineKeyboardButton(text=ch['name'], url=ch['link']))
    keyboard.add(InlineKeyboardButton("✅ Verify", callback_data="verify_join"))
    return keyboard

def country_list_keyboard(countries):
    """API থেকে আসা রিয়েল দেশের লিস্ট দিয়ে বাটন বানাবে"""
    keyboard = InlineKeyboardMarkup(row_width=1)
    # countries লিস্টে (name, qty, country_code) থাকবে API থেকে
    for name, qty, code in countries:
        btn_text = f"{name} ({qty})"
        keyboard.add(InlineKeyboardButton(text=btn_text, callback_data=f"buy_{code}"))
    
    keyboard.add(InlineKeyboardButton("🔙 Back to Menu", callback_data="back_to_main"))
    return keyboard

def number_action_keyboard(order_id):
    """নাম্বার কেনার পর রিয়েল অর্ডার আইডি দিয়ে বাটন বানাবে"""
    keyboard = InlineKeyboardMarkup(row_width=2)
    
    btn_view_otp = InlineKeyboardButton("📥 View OTP", callback_data=f"view_otp_{order_id}")
    btn_change_number = InlineKeyboardButton("🔄 Change Number", callback_data=f"change_{order_id}")
    btn_change_country = InlineKeyboardButton("🌍 Change Country", callback_data="show_countries")
    
    keyboard.add(btn_view_otp)
    keyboard.add(btn_change_number, btn_change_country)
    return keyboard

def admin_main_keyboard():
    keyboard = InlineKeyboardMarkup(row_width=2)
    
    # URL এর মাধ্যমে সরাসরি চ্যানেল/গ্রুপ অ্যাড করার অপশন (ভিডিওর মতো)
    # এখানে 'your_bot_username' এর জায়গায় আপনার বটের আসল ইউজারনেম দিবেন (যেমন: VirtualNumHub_bot)
    add_channel_btn = InlineKeyboardButton(
        "➕ Add Channel", 
        url="https://t.me/VirtualNumHub_bot?startchannel=true&admin=invite_users+post_messages"
    )
    
    add_otp_group_btn = InlineKeyboardButton(
        "➕ Add OTP Group", 
        url="https://t.me/VirtualNumHub_bot?startgroup=true&admin=invite_users+post_messages"
    )
    
    keyboard.add(add_channel_btn, InlineKeyboardButton("➖ Remove Channel", callback_data="admin_rm_ch"))
    keyboard.add(add_otp_group_btn, InlineKeyboardButton("➖ Remove OTP Group", callback_data="admin_rm_otp"))
    keyboard.add(InlineKeyboardButton("📢 Broadcast Message", callback_data="admin_broadcast"))
    
    return keyboard