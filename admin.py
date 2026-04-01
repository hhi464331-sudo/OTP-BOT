from aiogram import types, Dispatcher
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup
import config
import database as db
import keyboards.inline as inline_kb

class AdminStates(StatesGroup):
    waiting_for_channel_info = State()
    waiting_for_otp_group_id = State()
    waiting_for_broadcast = State()

async def admin_panel(message: types.Message):
    if message.from_user.id != config.ADMIN_ID: return
    await message.answer("👑 <b>Admin Control Panel</b>\nSelect an option below:", parse_mode='HTML', reply_markup=inline_kb.admin_main_keyboard())

# --- Add Channel Logic ---
async def ask_channel_info(callback_query: types.CallbackQuery):
    text = (
        "<b>চ্যানেল অ্যাড করার নিয়ম:</b>\n"
        "প্রথমে চ্যানেলের ID, তারপর লিংক, তারপর নাম দিন। মাঝখানে কমা (,) দিবেন।\n\n"
        "<b>উদাহরণ (এভাবে কপি করে বসান):</b>\n"
        "<code>-10012345678, https://t.me/mychannel, My Channel</code>"
    )
    await callback_query.message.answer(text, parse_mode='HTML')
    await AdminStates.waiting_for_channel_info.set()

async def save_channel_info(message: types.Message, state: FSMContext):
    try:
        parts = message.text.split(',')
        if len(parts) != 3:
            raise ValueError
        chat_id = int(parts[0].strip())
        link = parts[1].strip()
        name = parts[2].strip()
        
        await db.add_channel(chat_id, link, name)
        await message.answer("✅ <b>Channel Added successfully!</b>", parse_mode='HTML')
    except:
        await message.answer("❌ <b>ভুল ফরম্যাট!</b> দয়া করে কমা (,) দিয়ে ৩টি তথ্য ঠিকভাবে দিন।", parse_mode='HTML')
    await state.finish()

# --- Add OTP Group Logic ---
async def ask_otp_group(callback_query: types.CallbackQuery):
    await callback_query.message.answer("<b>OTP গ্রুপের ID দিন:</b>\nযেমন: <code>-100987654321</code>", parse_mode='HTML')
    await AdminStates.waiting_for_otp_group_id.set()

async def save_otp_group(message: types.Message, state: FSMContext):
    try:
        chat_id = int(message.text.strip())
        await db.add_otp_group(chat_id)
        await message.answer("✅ <b>OTP Group Added successfully!</b>", parse_mode='HTML')
    except:
        await message.answer("❌ <b>ভুল ID!</b> শুধুমাত্র সংখ্যা দিন।", parse_mode='HTML')
    await state.finish()

def register_admin_handlers(dp: Dispatcher):
    dp.register_message_handler(admin_panel, commands=['admin'])
    
    dp.register_callback_query_handler(ask_channel_info, lambda c: c.data == 'admin_add_ch')
    dp.register_message_handler(save_channel_info, state=AdminStates.waiting_for_channel_info)
    
    dp.register_callback_query_handler(ask_otp_group, lambda c: c.data == 'admin_add_otp')
    dp.register_message_handler(save_otp_group, state=AdminStates.waiting_for_otp_group_id)