import asyncio
from aiogram import types, Dispatcher
from aiogram.dispatcher.filters import Text
from aiogram.utils.exceptions import MessageNotModified
import database as db
import api
import keyboards.inline as inline_kb
import keyboards.reply as reply_kb

async def force_join_check(message_or_call):
    is_online = await db.is_system_online()
    user_id = message_or_call.from_user.id
    
    # Anti-Spam Check (2 সেকেন্ড ওয়েট লজিক)
    if await db.check_spam(user_id):
        if isinstance(message_or_call, types.CallbackQuery):
            await message_or_call.answer("⏳ Please wait 2 seconds! (Spam Protection)", show_alert=True)
        else:
            await message_or_call.answer("⏳ <b>Please wait 2 seconds before clicking again!</b>", parse_mode='HTML')
        return False

    if not is_online and user_id != config.ADMIN_ID:
        if isinstance(message_or_call, types.CallbackQuery): 
            await message_or_call.answer("Maintenance Mode!", show_alert=True)
        else: 
            await message_or_call.answer("⚠️ <b>Bot is under maintenance.</b>", parse_mode='HTML')
        return False

    # (Force Join checking logic here as before...)
    return True

# --- NEW: View OTP Pop-up Logic ---
async def view_otp_list(callback_query: types.CallbackQuery):
    if not await force_join_check(callback_query): return
    
    data = callback_query.data.split('_')
    order_id = data[3]
    country_code = data[4]
    
    otp_channels = await db.get_otp_channels()
    otp_groups = await db.get_otp_groups()
    all_sources = otp_channels + otp_groups
    
    if not all_sources:
        return await callback_query.answer("❌ No OTP sources available!", show_alert=True)
        
    await callback_query.message.edit_text(
        "<b>📩 Select to View OTP:</b>", 
        parse_mode='HTML', 
        reply_markup=inline_kb.view_otp_sources_keyboard(all_sources, order_id, country_code)
    )

# --- NEW: Back Button Glitch Fix ---
async def back_to_order_ui(callback_query: types.CallbackQuery):
    """Back বাটনে চাপ দিলে মেইন মেনুতে না গিয়ে আগের নাম্বারে ফেরত আসবে"""
    if not await force_join_check(callback_query): return
    
    data = callback_query.data.split('_')
    order_id = data[3]
    country_code = data[4]
    
    order = await db.orders_col.find_one({"order_id": order_id})
    if not order:
        return await callback_query.answer("❌ Session Expired or OTP already received!", show_alert=True)
        
    phone = order['phone']
    msg_text = f"""
🇻🇳 <b>{country_code.upper()} WS Fresh Number:</b>

📱 <b>Your Number:</b>
└ <code>+{phone}</code> ──┘

┌─────────────────────────┐
    ⏳ <b>Waiting For OTP...</b>
└─────────────────────────┘

<blockquote>📢 <i>এই নাম্বারে OTP পাঠানোর পর বটেই OTP পাবেন। যদি বটে OTP না আসে তাহলে OTP গ্রুপে পাবেন।</i> 🌸
🔸 ────Stay With Us──── 🔸</blockquote>
"""
    await callback_query.message.edit_text(msg_text, parse_mode='HTML', reply_markup=inline_kb.number_action_keyboard(order_id, country_code))

# --- NEW: Cancel Logic (Save for Group) ---
async def cancel_number_action(callback_query: types.CallbackQuery):
    if not await force_join_check(callback_query): return
    data = callback_query.data.split('_')
    order_id = data[1]
    
    # ডিলিট না করে abandoned করে দিচ্ছি, যাতে ব্যাকগ্রাউন্ড চেকার ওটিপি পেলে গ্রুপে পাঠাতে পারে!
    await db.update_order_status(order_id, "abandoned")
    await api.cancel_number(order_id) # API তে ক্যানসেল
    
    await callback_query.message.edit_text("❌ <b>Number Cancelled!</b>\n(If OTP arrives late, it will be sent to our public group).", parse_mode='HTML')

def register_user_handlers(dp: Dispatcher):
    dp.register_callback_query_handler(view_otp_list, lambda c: c.data.startswith('view_otp_list_'))
    dp.register_callback_query_handler(back_to_order_ui, lambda c: c.data.startswith('back_to_order_'))
    dp.register_callback_query_handler(cancel_number_action, lambda c: c.data.startswith('cancel_'))
    # (Register other handlers...)