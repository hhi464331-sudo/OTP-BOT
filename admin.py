from aiogram import types, Dispatcher
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup
import config
import database as db
import keyboards.inline as inline_kb
from aiogram.types import ChatMemberUpdated

class AdminStates(StatesGroup):
    waiting_for_broadcast = State()

async def admin_panel(message: types.Message):
    if message.from_user.id != config.ADMIN_ID: return
    await message.answer("👑 <b>Admin Control Panel</b>\nSelect an option below:", parse_mode='HTML', reply_markup=inline_kb.admin_main_keyboard())

# ==========================================
# Auto-Add Button Generators (Magic Links)
# ==========================================
async def ask_channel_info(callback_query: types.CallbackQuery):
    bot_info = await callback_query.bot.me
    markup = types.InlineKeyboardMarkup()
    # টেলিগ্রামের ডিফল্ট Add to Channel বাটন
    markup.add(types.InlineKeyboardButton("➕ Add Bot to Channel", url=f"https://t.me/{bot_info.username}?startchannel=true"))
    
    text = "✅ <b>Force Join চ্যানেল অ্যাড করতে নিচের বাটনে চাপ দিন:</b>\n\nচ্যানেল সিলেক্ট করে বটকে শুধু অ্যাডমিন বানিয়ে দিন, বাকিটা বট নিজে ডাটাবেসে সেভ করে নেবে!"
    await callback_query.message.answer(text, reply_markup=markup, parse_mode='HTML')
    await callback_query.answer()

async def ask_otp_group(callback_query: types.CallbackQuery):
    bot_info = await callback_query.bot.me
    markup = types.InlineKeyboardMarkup()
    # টেলিগ্রামের ডিফল্ট Add to Group বাটন
    markup.add(types.InlineKeyboardButton("➕ Add Bot to Group", url=f"https://t.me/{bot_info.username}?startgroup=true"))
    
    text = "✅ <b>OTP গ্রুপ অ্যাড করতে নিচের বাটনে চাপ দিন:</b>\n\nগ্রুপ সিলেক্ট করে বটকে অ্যাডমিন বানিয়ে দিন, বাকিটা বট নিজে ডাটাবেসে সেভ করে নেবে!"
    await callback_query.message.answer(text, reply_markup=markup, parse_mode='HTML')
    await callback_query.answer()

# ==========================================
# Bot Added Event Listener (This saves the data)
# ==========================================
async def bot_added_to_chat(update: ChatMemberUpdated):
    """বটকে কোথাও অ্যাড করা হলে এই ফাংশন অটোমেটিক কাজ করবে"""
    # যদি অন্য কেউ আপনার বটকে তাদের গ্রুপে অ্যাড করে, বট সাথে সাথে বের হয়ে যাবে
    if update.from_user.id != config.ADMIN_ID:
        await update.bot.leave_chat(update.chat.id)
        return
        
    if update.new_chat_member.status in ['administrator', 'member']:
        chat = update.chat
        try:
            if chat.type == 'channel':
                # প্রাইভেট চ্যানেল হলেও বট অটোমেটিক লিংক জেনারেট করে সেভ করবে
                link = f"https://t.me/{chat.username}" if chat.username else await chat.export_invite_link()
                await db.add_channel(chat.id, link, chat.title)
                await update.bot.send_message(config.ADMIN_ID, f"✅ <b>Channel Successfully Added!</b>\n📌 Name: {chat.title}", parse_mode='HTML')
                
            elif chat.type in ['group', 'supergroup']:
                await db.add_otp_group(chat.id)
                await update.bot.send_message(config.ADMIN_ID, f"✅ <b>OTP Group Successfully Added!</b>\n📌 Name: {chat.title}", parse_mode='HTML')
        except Exception as e:
            await update.bot.send_message(config.ADMIN_ID, f"❌ <b>Error:</b> {e}", parse_mode='HTML')

# ==========================================
# Broadcast Logic
# ==========================================
async def ask_broadcast_msg(callback_query: types.CallbackQuery):
    await callback_query.message.answer("<b>Send the message you want to broadcast to all users:</b>\n<i>Send /cancel to abort.</i>", parse_mode='HTML')
    await AdminStates.waiting_for_broadcast.set()

async def send_broadcast(message: types.Message, state: FSMContext):
    if message.text == '/cancel':
        await state.finish()
        await message.answer("❌ Broadcast cancelled.")
        return
        
    users = await db.get_all_users()
    success = 0
    for user in users:
        try:
            await message.bot.send_message(user['user_id'], message.text)
            success += 1
        except: pass
    await message.answer(f"📢 Broadcast sent to {success} users successfully!")
    await state.finish()

def register_admin_handlers(dp: Dispatcher):
    dp.register_message_handler(admin_panel, commands=['admin'])
    dp.register_callback_query_handler(ask_channel_info, lambda c: c.data == 'admin_add_ch')
    dp.register_callback_query_handler(ask_otp_group, lambda c: c.data == 'admin_add_otp')
    dp.register_callback_query_handler(ask_broadcast_msg, lambda c: c.data == 'admin_broadcast')
    dp.register_message_handler(send_broadcast, state=AdminStates.waiting_for_broadcast)
    # Magic Handler for auto detecting chat:
    dp.register_my_chat_member_handler(bot_added_to_chat)