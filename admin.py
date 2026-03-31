from aiogram import types, Dispatcher
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup
import config
import database as db
import keyboards.inline as inline_kb

class AdminStates(StatesGroup):
    waiting_for_channel_id = State()
    waiting_for_otp_group_id = State()
    waiting_for_broadcast = State()

async def admin_panel(message: types.Message):
    """শুধু আসল অ্যাডমিন এই প্যানেল দেখতে পারবে"""
    if message.from_user.id != config.ADMIN_ID:
        return # অন্য কেউ দিলে ইগনোর করবে
    await message.answer("👑 <b>Admin Control Panel</b>\nSelect an option below:", reply_markup=inline_kb.admin_main_keyboard())

# --- Add Channel Logic ---
async def ask_channel_info(callback_query: types.CallbackQuery):
    await callback_query.message.answer("Send Channel ID, Link, and Name separated by comma.\nFormat: `-100123, t.me/link, Channel Name`")
    await AdminStates.waiting_for_channel_id.set()

async def save_channel_info(message: types.Message, state: FSMContext):
    try:
        parts = message.text.split(',')
        chat_id = int(parts[0].strip())
        link = parts[1].strip()
        name = parts[2].strip()
        await db.add_channel(chat_id, link, name)
        await message.answer("✅ Channel Added successfully!")
    except:
        await message.answer("❌ Invalid format.")
    await state.finish()

# --- Broadcast Logic ---
async def ask_broadcast_msg(callback_query: types.CallbackQuery):
    await callback_query.message.answer("Send the message you want to broadcast to all users:")
    await AdminStates.waiting_for_broadcast.set()

async def send_broadcast(message: types.Message, state: FSMContext):
    users = await db.get_all_users()
    success = 0
    for user in users:
        try:
            await message.bot.send_message(user['user_id'], message.text)
            success += 1
        except:
            pass # যদি কেউ বট ব্লক করে রাখে
    await message.answer(f"📢 Broadcast sent to {success} users successfully!")
    await state.finish()

def register_admin_handlers(dp: Dispatcher):
    dp.register_message_handler(admin_panel, commands=['admin'])
    
    dp.register_callback_query_handler(ask_channel_info, lambda c: c.data == 'admin_add_ch')
    dp.register_message_handler(save_channel_info, state=AdminStates.waiting_for_channel_id)
    
    dp.register_callback_query_handler(ask_broadcast_msg, lambda c: c.data == 'admin_broadcast')
    dp.register_message_handler(send_broadcast, state=AdminStates.waiting_for_broadcast)