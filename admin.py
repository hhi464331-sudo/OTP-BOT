from aiogram import types, Dispatcher
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.dispatcher.filters import Text
import config
import database as db
import keyboards.inline as inline_kb

class AdminStates(StatesGroup):
    waiting_for_broadcast = State()

async def admin_panel(message: types.Message):
    if message.from_user.id != config.ADMIN_ID: return
    await message.answer(
        "👑 <b>Admin Control Panel</b>\n"
        "Select an option below:\n\n"
        "<i>Note: To add a channel or group, just click the button and add the bot as an admin.</i>", 
        parse_mode='HTML', 
        reply_markup=inline_kb.admin_main_keyboard()
    )

# --- Auto Save Logic (যখন বটকে কোনো গ্রুপ/চ্যানেলে অ্যাড করা হবে) ---
async def bot_added_to_chat(message: types.Message):
    """বট নিজে থেকে চ্যানেল বা গ্রুপে অ্যাড হলে ডাটাবেসে সেভ হবে"""
    chat_type = message.chat.type
    chat_id = message.chat.id
    chat_title = message.chat.title
    
    # যদি চ্যানেল হয় (Force Join এর জন্য)
    if chat_type == 'channel':
        # চ্যানেলের লিংক জেনারেট করার ট্রাই করবে
        try:
            link = await message.bot.export_chat_invite_link(chat_id)
        except:
            link = "Link missing (need admin rights)"
            
        await db.add_channel(chat_id, link, chat_title)
        # আপনাকে ইনবক্সে কনফার্ম করবে
        await message.bot.send_message(config.ADMIN_ID, f"✅ <b>Channel Auto-Added!</b>\nName: {chat_title}\nID: <code>{chat_id}</code>", parse_mode='HTML')

    # যদি গ্রুপ হয় (OTP Group এর জন্য)
    elif chat_type in ['group', 'supergroup']:
        await db.add_otp_group(chat_id)
        await message.bot.send_message(config.ADMIN_ID, f"✅ <b>OTP Group Auto-Added!</b>\nName: {chat_title}\nID: <code>{chat_id}</code>", parse_mode='HTML')


# --- Broadcast Logic ---
async def ask_broadcast_msg(callback_query: types.CallbackQuery):
    await callback_query.message.answer("<b>Send the message to broadcast to all users:</b>\nSend /cancel to abort.", parse_mode='HTML')
    await AdminStates.waiting_for_broadcast.set()

async def send_broadcast(message: types.Message, state: FSMContext):
    if message.text == '/cancel':
        await message.answer("❌ Broadcast cancelled.")
        await state.finish()
        return
        
    users = await db.get_all_users()
    success = 0
    for user in users:
        try:
            await message.bot.send_message(user['user_id'], message.text)
            success += 1
        except:
            pass
            
    await message.answer(f"📢 <b>Broadcast complete!</b>\n✅ Sent: {success}\n❌ Failed: {len(users)-success}", parse_mode='HTML')
    await state.finish()


def register_admin_handlers(dp: Dispatcher):
    dp.register_message_handler(admin_panel, commands=['admin'])
    
    # Broadcast handlers
    dp.register_callback_query_handler(ask_broadcast_msg, lambda c: c.data == 'admin_broadcast')
    dp.register_message_handler(send_broadcast, state=AdminStates.waiting_for_broadcast)
    
    # Bot added to chat handler (অটোমেটিক সেভ হওয়ার জন্য)
    dp.register_message_handler(bot_added_to_chat, content_types=['new_chat_members'])