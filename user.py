from aiogram import types, Dispatcher
from aiogram.dispatcher.filters import Text
import database as db
import api
from utils import is_overloaded, add_req, remove_req
import keyboards.reply as reply_kb
import keyboards.inline as inline_kb

async def show_countries(message: types.Message):
    """API থেকে রিয়েল কান্ট্রি লিস্ট দেখাবে"""
    if is_overloaded():
        await message.answer("⚠️ সার্ভার এখন বিজি আছে, অনুগ্রহ করে ০.৫ সেকেন্ড পর আবার চেষ্টা করুন।")
        return
    
    await add_req()
    try:
        loading_msg = await message.answer("⏳ Fetching live countries from API...")
        countries = await api.get_countries() # রিয়েল API কল
        
        if not countries:
            await loading_msg.edit_text("❌ Currently no numbers available in the API.")
            return
            
        await loading_msg.edit_text("🌍 Select Country:", reply_markup=inline_kb.country_list_keyboard(countries))
    finally:
        await remove_req()

async def buy_number_handler(callback_query: types.CallbackQuery):
    """API থেকে রিয়েল নাম্বার কেনার লজিক"""
    if is_overloaded():
        await callback_query.answer("⚠️ সার্ভার বিজি, একটু পর আবার ট্রাই করুন।", show_alert=True)
        return
        
    await add_req()
    try:
        user_id = callback_query.from_user.id
        country_code = callback_query.data.split('_')[1]
        
        await callback_query.message.edit_text("⏳ Processing your request with API...")
        
        # API থেকে নাম্বার কেনা
        order = await api.buy_number(country_code)
        
        if not order:
            await callback_query.message.edit_text("❌ Failed to get a number. Please try another country.", reply_markup=inline_kb.country_list_keyboard(await api.get_countries()))
            return
            
        order_id = order['order_id']
        phone = order['phone']
        
        # ডাটাবেসে সেভ (active স্ট্যাটাস)
        await db.save_order(user_id, order_id, phone, country_code)
        
        # আপনার স্ক্রিনশটের হুবহু মেসেজ ডিজাইন
        msg_text = f"""
🇸🇩 <b>{country_code.upper()} Fresh Number Assigned:</b>

📱 <b>Your Number:</b>
└ <code>+{phone}</code> ──┘

┌─────────────────────────┐
    ⏳ <b>Waiting For OTP...</b>
└─────────────────────────┘

📢 <i>এই নাম্বারে OTP পাঠানোর পর বটেই OTP পাবেন। যদি বটে OTP না আসে তাহলে OTP গ্রুপে OTP পাবেন।</i> 🌸
🔸 ────Stay With Us──── 🔸
"""
        await callback_query.message.edit_text(msg_text, reply_markup=inline_kb.number_action_keyboard(order_id))
    finally:
        await remove_req()

async def change_number_handler(callback_query: types.CallbackQuery):
    """নাম্বার চেঞ্জ করলে আগেরটাকে abandoned করে দিবে"""
    order_id = callback_query.data.split('_')[1]
    
    # ডাটাবেসে স্ট্যাটাস আপডেট (late OTP লজিকের জন্য)
    await db.orders_col.update_one({"order_id": order_id}, {"$set": {"status": "abandoned"}})
    
    await callback_query.answer("🔄 Number Changed! Check available countries.", show_alert=True)
    await show_countries(callback_query.message) # আবার কান্ট্রি লিস্ট দিবে

async def manual_otp_check(callback_query: types.CallbackQuery):
    """View OTP বাটনে চাপ দিলে ম্যানুয়ালি চেক করবে"""
    order_id = callback_query.data.split('_')[2]
    otp = await api.check_otp_status(order_id)
    
    if otp:
        await callback_query.answer(f"✅ Your OTP is: {otp}", show_alert=True)
    else:
        await callback_query.answer("⏳ OTP not received yet. Please wait.", show_alert=True)

async def support_info(message: types.Message):
    await message.answer("☎️ Contact support:", reply_markup=inline_kb.support_keyboard())

def register_user_handlers(dp: Dispatcher):
    dp.register_message_handler(show_countries, Text(equals=["📱 Get Number", "🌍 Available Country"]))
    dp.register_message_handler(support_info, Text(equals="☎️ Support"))
    dp.register_callback_query_handler(buy_number_handler, lambda c: c.data and c.data.startswith('buy_'))
    dp.register_callback_query_handler(change_number_handler, lambda c: c.data and c.data.startswith('change_'))
    dp.register_callback_query_handler(manual_otp_check, lambda c: c.data and c.data.startswith('view_otp_'))