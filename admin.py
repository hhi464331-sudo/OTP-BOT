import io
from aiogram import types, Dispatcher
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.types import ChatMemberUpdated, InlineKeyboardMarkup, InlineKeyboardButton
import config
import database as db
import keyboards.inline as inline_kb

class AdminStates(StatesGroup):
    waiting_for_broadcast = State()
    adding_fj_ch = State()
    adding_fj_gr = State()
    adding_otp_ch = State()
    adding_otp_gr = State()

async def admin_panel(message: types.Message):
    if message.from_user.id != config.ADMIN_ID: return
    is_online = await db.is_system_online()
    await message.answer("👑 <b>Admin Control Panel</b>\nSelect an option below:", parse_mode='HTML', reply_markup=inline_kb.admin_main_keyboard(is_online))

# --- Magic Add System ---
async def start_adding(callback_query: types.CallbackQuery, state: FSMContext):
    action = callback_query.data
    bot_info = await callback_query.bot.me
    
    if action == "add_fj_ch":
        await AdminStates.adding_fj_ch.set()
        url = f"https://t.me/{bot_info.username}?startchannel=true"
        text = "📢 <b>Force Join Channel</b> অ্যাড করতে নিচের বাটনে চাপ দিন:"
    elif action == "add_fj_gr":
        await AdminStates.adding_fj_gr.set()
        url = f"https://t.me/{bot_info.username}?startgroup=true"
        text = "👥 <b>Force Join Group</b> অ্যাড করতে নিচের বাটনে চাপ দিন:"
    elif action == "add_otp_ch":
        await AdminStates.adding_otp_ch.set()
        url = f"https://t.me/{bot_info.username}?startchannel=true"
        text = "📨 <b>OTP Channel</b> অ্যাড করতে নিচের বাটনে চাপ দিন:"
    elif action == "add_otp_gr":
        await AdminStates.adding_otp_gr.set()
        url = f"https://t.me/{bot_info.username}?startgroup=true"
        text = "📨 <b>OTP Group</b> অ্যাড করতে নিচের বাটনে চাপ দিন:"

    markup = InlineKeyboardMarkup().add(InlineKeyboardButton("➕ Add Bot to Chat", url=url))
    await callback_query.message.answer(text, reply_markup=markup, parse_mode='HTML')

# --- Save ID Automatically Based on State ---
async def bot_added_to_chat(update: ChatMemberUpdated):
    if update.from_user.id != config.ADMIN_ID:
        await update.bot.leave_chat(update.chat.id)
        return
        
    if update.new_chat_member.status in ['administrator', 'member']:
        chat = update.chat
        dp = Dispatcher.get_current()
        state = dp.current_state(chat=config.ADMIN_ID, user=config.ADMIN_ID)
        current_state = await state.get_state()
        
        try:
            link = f"https://t.me/{chat.username}" if chat.username else await chat.export_invite_link()
            
            if current_state == "AdminStates:adding_fj_ch":
                await db.add_fj_channel(chat.id, link, chat.title)
                cat = "Force Join Channel"
            elif current_state == "AdminStates:adding_fj_gr":
                await db.add_fj_group(chat.id, link, chat.title)
                cat = "Force Join Group"
            elif current_state == "AdminStates:adding_otp_ch":
                await db.add_otp_channel(chat.id, link, chat.title)
                cat = "OTP Channel"
            elif current_state == "AdminStates:adding_otp_gr":
                await db.add_otp_group(chat.id, link, chat.title)
                cat = "OTP Group"
            else:
                return # Ignore if not in adding state
                
            await update.bot.send_message(config.ADMIN_ID, f"✅ <b>{cat} Added!</b>\n📌 {chat.title}", parse_mode='HTML')
            await state.finish()
        except Exception as e:
            pass

# --- Remove Handlers (Shortened for brevity) ---
async def remove_item_list(callback_query: types.CallbackQuery):
    action = callback_query.data
    markup = InlineKeyboardMarkup(row_width=1)
    
    if action == "rm_fj_ch":
        items = await db.get_fj_channels()
        for i in items: markup.add(InlineKeyboardButton(f"❌ {i['name']}", callback_data=f"del_fjc_{i['chat_id']}"))
    elif action == "rm_fj_gr":
        items = await db.get_fj_groups()
        for i in items: markup.add(InlineKeyboardButton(f"❌ {i['name']}", callback_data=f"del_fjg_{i['chat_id']}"))
    elif action == "rm_otp_ch":
        items = await db.get_otp_channels()
        for i in items: markup.add(InlineKeyboardButton(f"❌ {i['name']}", callback_data=f"del_otpc_{i['chat_id']}"))
    elif action == "rm_otp_gr":
        items = await db.get_otp_groups()
        for i in items: markup.add(InlineKeyboardButton(f"❌ {i['name']}", callback_data=f"del_otpg_{i['chat_id']}"))
        
    if not items: return await callback_query.answer("No items found!", show_alert=True)
    await callback_query.message.answer("<b>Select item to remove:</b>", reply_markup=markup, parse_mode='HTML')

async def execute_remove(callback_query: types.CallbackQuery):
    data = callback_query.data.split('_')
    cat, chat_id = data[1], int(data[2])
    
    if cat == "fjc": await db.remove_fj_channel(chat_id)
    elif cat == "fjg": await db.remove_fj_group(chat_id)
    elif cat == "otpc": await db.remove_otp_channel(chat_id)
    elif cat == "otpg": await db.remove_otp_group(chat_id)
    
    await callback_query.message.edit_text("✅ Removed Successfully!")

# --- Broadcast, Stats, Power ---
async def ask_broadcast(c: types.CallbackQuery):
    await c.message.answer("<b>Send your message:</b>", parse_mode='HTML')
    await AdminStates.waiting_for_broadcast.set()

async def send_broadcast(m: types.Message, state: FSMContext):
    users = await db.get_all_users()
    for u in users:
        try: await m.copy_to(u['user_id'])
        except: pass
    await m.answer("📢 Broadcast Complete!")
    await state.finish()

async def stats(c: types.CallbackQuery):
    t = await db.get_users_count()
    await c.message.answer(f"📊 <b>Total Users:</b> {t}", parse_mode='HTML')

async def toggle_power(c: types.CallbackQuery):
    status = not await db.is_system_online()
    await db.toggle_system_power(status)
    await c.message.edit_reply_markup(inline_kb.admin_main_keyboard(status))

def register_admin_handlers(dp: Dispatcher):
    dp.register_message_handler(admin_panel, commands=['admin'], chat_type=types.ChatType.PRIVATE)
    dp.register_callback_query_handler(start_adding, lambda c: c.data.startswith('add_'))
    dp.register_callback_query_handler(remove_item_list, lambda c: c.data.startswith('rm_'))
    dp.register_callback_query_handler(execute_remove, lambda c: c.data.startswith('del_'))
    dp.register_callback_query_handler(ask_broadcast, lambda c: c.data == 'admin_broadcast')
    dp.register_message_handler(send_broadcast, state=AdminStates.waiting_for_broadcast, content_types=types.ContentTypes.ANY, chat_type=types.ChatType.PRIVATE)
    dp.register_callback_query_handler(stats, lambda c: c.data == 'admin_stats')
    dp.register_callback_query_handler(toggle_power, lambda c: c.data == 'admin_power_toggle')
    dp.register_my_chat_member_handler(bot_added_to_chat)