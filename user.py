import asyncio
from aiogram import types, Dispatcher
from aiogram.dispatcher.filters import Text
from aiogram.utils.exceptions import MessageNotModified, MessageToDeleteNotFound
import database as db
import api
from utils import is_overloaded, add_req, remove_req
import keyboards.reply as reply_kb
import keyboards.inline as inline_kb

user_last_msg = {}

async def delete_previous_bot_message(user_id, bot):
    if user_id in user_last_msg:
        try:
            await bot.delete_message(chat_id=user_id, message_id=user_last_msg[user_id])
        except MessageToDeleteNotFound:
            pass
        except Exception:
            pass

async def show_countries_handler(message_or_call):
    if is_overloaded(): return
    await add_req()
    try:
        user_id = message_or_call.from_user.id
        bot = message_or_call.bot
        
        countries = await api.get_countries()
        text = "🌍 <b>Select Country:</b>" if countries else "❌ <b>Currently no numbers available.</b>"
        
        if isinstance(message_or_call, types.CallbackQuery):
            # Change Country বা Back বাটনে চাপ দিলে শুধু এডিট হবে
            try:
                await message_or_call.message.edit_text(text, parse_mode='HTML', reply_markup=inline_kb.country_list_keyboard(countries))
            except MessageNotModified:
                pass 
        else:
            # Menu থেকে চাপ দিলে আগের মেসেজ ডিলিট হবে, নতুন মেসেজ আসবে (ভিডিওর মতো)
            await delete_previous_bot_message(user_id, bot)
            msg = await message_or_call.answer(text, parse_mode='HTML', reply_markup=inline_kb.country_list_keyboard(countries))
            user_last_msg[user_id] = msg.message_id
            try: await message_or_call.delete() except: pass
    finally:
        await remove_req()

async def get_number_logic(message, country_code, is_change=False):
    order = await api.buy_number(country_code)
    
    if not order:
        await message.edit_text("❌ <b>Failed to get a number.</b>", parse_mode='HTML', reply_markup=inline_kb.country_list_keyboard(await api.get_countries()))
        return
        
    order_id = order['order_id']
    phone = str(order['phone']).replace('+', '') 
    
    await db.save_order(message.chat.id, order_id, phone, country_code)
    
    title_text = "Fresh Number Changed:" if is_change else "Fresh Number Assigned:"
    
    msg_text = f"""
🇸🇩 <b>{country_code.upper()} FB {title_text}</b>

📱 <b>Your Number:</b>
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
    if is_overloaded(): return
    await add_req()
    try:
        country_code = callback_query.data.split('_')[1]
        # কান্ট্রি সিলেক্ট করলে ওই মেসেজটাই এডিট হয়ে Assigning Number আসবে
        await callback_query.message.edit_text("⏳ <b>Assigning number...</b>", parse_mode='HTML')
        await get_number_logic(callback_query.message, country_code)
    finally:
        await remove_req()

async def change_number_handler(callback_query: types.CallbackQuery):
    if is_overloaded(): return
    
    data_parts = callback_query.data.split('_')
    old_order_id = data_parts[1]
    country_code = data_parts[2]
    
    await db.orders_col.update_one({"order_id": old_order_id}, {"$set": {"status": "abandoned"}})
    
    await add_req()
    try:
        # ভিডিওর মতো হুবহু লজিক: আগের মেসেজ এডিট হবে না, নতুন মেসেজ সেন্ড হবে
        anim_msg = await callback_query.message.answer("⏳ <b>Changing Number...</b>", parse_mode='HTML')
        await asyncio.sleep(0.5)
        await anim_msg.edit_text("⏳ <b>Finding fresh line...</b>", parse_mode='HTML')
        await asyncio.sleep(0.5)
        
        await get_number_logic(anim_msg, country_code, is_change=True)
    finally:
        await remove_req()

async def manual_otp_check(callback_query: types.CallbackQuery):
    order_id = callback_query.data.split('_')[2]
    otp = await api.check_otp_status(order_id)
    if otp:
        await callback_query.answer(f"✅ Your OTP is: {otp}", show_alert=True)
    else:
        # ভিডিওর মতো হুবহু পপআপ মেসেজ
        await callback_query.answer("⏳ Wait 1 second!", show_alert=True)

async def support_info(message: types.Message):
    user_id = message.from_user.id
    bot = message.bot
    await delete_previous_bot_message(user_id, bot)
    
    msg = await message.answer("☎️ <b>Contact support:</b>", parse_mode='HTML', reply_markup=inline_kb.support_keyboard())
    user_last_msg[user_id] = msg.message_id
    try: await message.delete() except: pass

def register_user_handlers(dp: Dispatcher):
    dp.register_message_handler(show_countries_handler, Text(equals=["📱 Get Number", "🌍 Available Country"]))
    dp.register_message_handler(support_info, Text(equals="☎️ Support"))
    dp.register_callback_query_handler(show_countries_handler, lambda c: c.data in ['show_countries', 'back_to_main'])
    dp.register_callback_query_handler(buy_number_handler, lambda c: c.data and c.data.startswith('buy_'))
    dp.register_callback_query_handler(change_number_handler, lambda c: c.data and c.data.startswith('change_'))
    dp.register_callback_query_handler(manual_otp_check, lambda c: c.data and c.data.startswith('view_otp_'))