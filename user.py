import asyncio
from aiogram import types, Dispatcher
from aiogram.dispatcher.filters import Text
from aiogram.utils.exceptions import MessageNotModified
import database as db
import api
from utils import get_wait_time, add_req, remove_req
import keyboards.inline as inline_kb

async def show_countries_handler(message_or_call):
    wait_time = get_wait_time()
    if wait_time > 0:
        if isinstance(message_or_call, types.CallbackQuery):
            await message_or_call.answer(f"⏳ Wait {wait_time} second!", show_alert=True)
        return

    await add_req()
    try:
        countries = await api.get_countries()
        text = "🌍 <b>Select Country:</b>" if countries else "❌ <b>Currently no numbers available.</b>"
        
        if isinstance(message_or_call, types.CallbackQuery):
            try:
                await message_or_call.message.edit_text(text, parse_mode='HTML', reply_markup=inline_kb.country_list_keyboard(countries))
            except MessageNotModified:
                pass 
        else:
            try: await message_or_call.delete() except: pass
            await message_or_call.answer(text, parse_mode='HTML', reply_markup=inline_kb.country_list_keyboard(countries))
    finally:
        await remove_req()

async def get_number_logic(message: types.Message, country_code, is_change=False):
    order = await api.buy_number(country_code)
    if not order:
        await message.edit_text("❌ <b>Failed to get a number.</b>", parse_mode='HTML', reply_markup=inline_kb.country_list_keyboard(await api.get_countries()))
        return
        
    order_id = order['order_id']
    phone = str(order['phone']).replace('+', '') 
    
    await db.save_order(message.chat.id, order_id, phone, country_code)
    
    title_text = "Fresh Number Changed:" if is_change else "Fresh Number Assigned:"
    msg_text = f"""
✅ Added Successfully!
🇵🇹 <b>{country_code.upper()} WS</b>
━━━━━━━━━━━━━━━━━━
📞 <b>Your Number:</b>
└ <code>{phone}</code> ──┘

┌─────────────────────────┐
    ⏳ <b>Waiting For OTP...</b>
└─────────────────────────┘

📢 <i>এই নাম্বারে OTP পাঠানোর পর বটেই OTP পাবেন। যদি বটে OTP না আসে তাহলে OTP গ্রুপে OTP পাবেন।</i> 🌸
🔸 ────Stay With Us──── 🔸
"""
    try:
        await message.edit_text(msg_text, parse_mode='HTML', reply_markup=inline_kb.number_action_keyboard(order_id, country_code))
    except MessageNotModified:
        pass

async def buy_number_handler(callback_query: types.CallbackQuery):
    wait_time = get_wait_time()
    if wait_time > 0:
        await callback_query.answer(f"⏳ Wait {wait_time} second!", show_alert=True)
        return

    # --- ACTIVE NUMBER CHECK LOGIC ---
    user_id = callback_query.from_user.id
    active_order = await db.orders_col.find_one({"user_id": user_id, "status": "active"})
    
    if active_order:
        # যদি একটিভ নাম্বার থাকে, তাহলে ভিডিওর মতো এরর মেসেজ দিবে
        phone = active_order['phone']
        order_id = active_order['order_id']
        country = active_order['country']
        error_msg = f"❌ <b>You have an active number:</b>\n📱 <code>{phone}</code>"
        
        await callback_query.answer("You have an active number!", show_alert=False)
        await callback_query.message.edit_text(error_msg, parse_mode='HTML', reply_markup=inline_kb.number_action_keyboard(order_id, country))
        return
    # ----------------------------------

    await add_req()
    try:
        country_code = callback_query.data.split('_')[1]
        await callback_query.message.edit_text("⏳ <b>Assigning number...</b>", parse_mode='HTML')
        await get_number_logic(callback_query.message, country_code)
    finally:
        await remove_req()

async def change_number_handler(callback_query: types.CallbackQuery):
    """Change Number: ভিডিওর মত শুধু নাম্বার চেঞ্জ হবে, কান্ট্রি সেম থাকবে"""
    wait_time = get_wait_time()
    if wait_time > 0:
        await callback_query.answer(f"⏳ Wait {wait_time} second!", show_alert=True)
        return

    data_parts = callback_query.data.split('_')
    old_order_id = data_parts[1]
    country_code = data_parts[2]
    
    # আগের নাম্বার ডাটাবেস থেকে বাতিল
    await db.orders_col.update_one({"order_id": old_order_id}, {"$set": {"status": "abandoned"}})
    await api.cancel_number(old_order_id)
    
    await add_req()
    try:
        # ভিডিওর মতো অ্যানিমেশন
        await callback_query.message.edit_text("🔄 <b>Changing Number...</b>", parse_mode='HTML')
        await asyncio.sleep(0.5)
        await callback_query.message.edit_text("⬇️ <b>Finding fresh line...</b>", parse_mode='HTML')
        
        # একই কান্ট্রির নতুন নাম্বার
        await get_number_logic(callback_query.message, country_code, is_change=True)
    finally:
        await remove_req()

async def change_country_handler(callback_query: types.CallbackQuery):
    """Change Country: নাম্বার বাতিল করে মেইন লিস্টে ফেরত যাবে"""
    order_id = callback_query.data.split('_')[1]
    
    # নাম্বার বাতিল
    await db.orders_col.update_one({"order_id": order_id}, {"$set": {"status": "abandoned"}})
    await api.cancel_number(order_id)
    
    await callback_query.answer("Number Cancelled!", show_alert=False)
    await show_countries_handler(callback_query)

async def manual_otp_check(callback_query: types.CallbackQuery):
    order_id = callback_query.data.split('_')[2]
    otp = await api.check_otp_status(order_id)
    if otp:
        await callback_query.answer(f"✅ Your OTP is: {otp}", show_alert=True)
    else:
        await callback_query.answer("⏳ OTP not received yet. Please wait!", show_alert=True)

SUPPORT_MSG_ID = {}
async def support_info(message: types.Message):
    user_id = message.from_user.id
    try: await message.delete() except: pass
    if user_id in SUPPORT_MSG_ID:
        try: await message.bot.delete_message(chat_id=user_id, message_id=SUPPORT_MSG_ID[user_id]) except: pass
    msg = await message.answer("☎️ <b>Contact support:</b>", parse_mode='HTML', reply_markup=inline_kb.support_keyboard())
    SUPPORT_MSG_ID[user_id] = msg.message_id

def register_user_handlers(dp: Dispatcher):
    dp.register_message_handler(show_countries_handler, Text(equals=["📱 Get Number", "🌍 Available Country"]))
    dp.register_message_handler(support_info, Text(equals="☎️ Support"))
    dp.register_callback_query_handler(show_countries_handler, lambda c: c.data == 'back_to_main')
    dp.register_callback_query_handler(buy_number_handler, lambda c: c.data and c.data.startswith('buy_'))
    dp.register_callback_query_handler(change_number_handler, lambda c: c.data and c.data.startswith('change_'))
    dp.register_callback_query_handler(change_country_handler, lambda c: c.data and c.data.startswith('cancel_'))
    dp.register_callback_query_handler(manual_otp_check, lambda c: c.data and c.data.startswith('view_otp_'))