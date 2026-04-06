import asyncio
from aiogram import types, Dispatcher
from aiogram.dispatcher.filters import Text
from aiogram.utils.exceptions import MessageNotModified
import database as db
import api
from utils import get_wait_time, add_req, remove_req
import keyboards.inline as inline_kb

async def check_membership(bot, user_id):
    """Force Join এর চ্যানেল এবং গ্রুপ চেক করবে"""
    fj_channels = await db.get_fj_channels()
    fj_groups = await db.get_fj_groups()
    
    for ch in fj_channels + fj_groups:
        try:
            member = await bot.get_chat_member(chat_id=ch['chat_id'], user_id=user_id)
            if member.status in ['left', 'kicked', 'restricted']: return False
        except: return False
    return True

async def force_join_check(message_or_call):
    """সিস্টেম চেক এবং Force Join ভেরিফাই করবে"""
    is_online = await db.is_system_online()
    user_id = message_or_call.from_user.id
    
    if not is_online and user_id != config.ADMIN_ID:
        if isinstance(message_or_call, types.CallbackQuery): await message_or_call.answer("Maintenance Mode!", show_alert=True)
        else: await message_or_call.answer("⚠️ <b>Bot is under maintenance.</b>", parse_mode='HTML')
        return False

    is_joined = await check_membership(message_or_call.bot, user_id)
    if not is_joined:
        fj_channels = await db.get_fj_channels()
        fj_groups = await db.get_fj_groups()
        text = "⚠️ <b>Access Denied!</b>\nPlease join required channels/groups."
        
        markup = inline_kb.force_join_keyboard(fj_channels, fj_groups)
        if isinstance(message_or_call, types.CallbackQuery):
            await message_or_call.message.answer(text, reply_markup=markup, parse_mode='HTML')
        else:
            await message_or_call.answer(text, reply_markup=markup, parse_mode='HTML')
        return False
    return True

# --- Verification Button Click ---
async def verify_join_btn(callback_query: types.CallbackQuery):
    if await check_membership(callback_query.bot, callback_query.from_user.id):
        await callback_query.message.delete()
        await callback_query.message.answer("✅ <b>Verification Successful!</b>", parse_mode='HTML')
        await show_countries_handler(callback_query)
    else:
        await callback_query.answer("❌ You haven't joined all required chats!", show_alert=True)

# --- View OTP Click (Show List) ---
async def view_otp_list(callback_query: types.CallbackQuery):
    if not await force_join_check(callback_query): return
    otp_channels = await db.get_otp_channels()
    otp_groups = await db.get_otp_groups()
    
    if not otp_channels and not otp_groups:
        return await callback_query.answer("❌ No OTP sources available!", show_alert=True)
        
    await callback_query.message.edit_text("<b>Select an OTP Channel/Group to view your OTP:</b>", parse_mode='HTML', reply_markup=inline_kb.view_otp_sources_keyboard(otp_channels, otp_groups))

# --- Main Functions ---
async def show_countries_handler(message_or_call):
    if not await force_join_check(message_or_call): return
    countries = await api.get_countries()
    text = "🌍 <b>Select Country:</b>" if countries else "❌ <b>Currently no numbers available.</b>"
    
    if isinstance(message_or_call, types.CallbackQuery):
        try: await message_or_call.message.edit_text(text, parse_mode='HTML', reply_markup=inline_kb.country_list_keyboard(countries))
        except MessageNotModified: pass 
    else:
        try: await message_or_call.delete() except: pass
        await message_or_call.answer(text, parse_mode='HTML', reply_markup=inline_kb.country_list_keyboard(countries))

async def get_number_logic(message: types.Message, country_code, is_change=False):
    order = await api.buy_number(country_code)
    if not order: return await message.edit_text("❌ Failed.", parse_mode='HTML')
    phone = str(order['phone']).replace('+', '') 
    await db.save_order(message.chat.id, order['order_id'], phone, country_code)
    msg_text = f"🇵🇹 <b>{country_code.upper()} WS</b>\n📞 <code>{phone}</code>\n\n<blockquote>⏳ Waiting for OTP...</blockquote>"
    await message.edit_text(msg_text, parse_mode='HTML', reply_markup=inline_kb.number_action_keyboard(order['order_id'], country_code))

async def buy_number_handler(callback_query: types.CallbackQuery):
    if not await force_join_check(callback_query): return
    country_code = callback_query.data.split('_')[1]
    await callback_query.message.edit_text("⏳ Assigning number...")
    await get_number_logic(callback_query.message, country_code)

async def change_country_handler(callback_query: types.CallbackQuery):
    if not await force_join_check(callback_query): return
    order_id = callback_query.data.split('_')[1]
    await db.orders_col.update_one({"order_id": order_id}, {"$set": {"status": "abandoned"}})
    await api.cancel_number(order_id)
    await show_countries_handler(callback_query)

def register_user_handlers(dp: Dispatcher):
    dp.register_message_handler(show_countries_handler, Text(equals=["📱 Get Number", "🌍 Available Country"]), chat_type=types.ChatType.PRIVATE)
    dp.register_callback_query_handler(verify_join_btn, lambda c: c.data == 'verify_join')
    dp.register_callback_query_handler(show_countries_handler, lambda c: c.data == 'back_to_main')
    dp.register_callback_query_handler(buy_number_handler, lambda c: c.data and c.data.startswith('buy_'))
    dp.register_callback_query_handler(change_country_handler, lambda c: c.data and c.data.startswith('cancel_'))
    dp.register_callback_query_handler(view_otp_list, lambda c: c.data and c.data.startswith('view_otp_list_'))