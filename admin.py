import io
from aiogram import types, Dispatcher
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup
import database as db
import keyboards.inline as inline_kb

class AdminStates(StatesGroup):
    waiting_for_broadcast = State()

def smart_formatter(text):
    """বটের স্মার্ট ব্রেইন: দাড়ি-কমা ছাড়া লিখলেও সুন্দর করে সাজিয়ে দিবে"""
    # কিওয়ার্ড রিপ্লেস (ইমোজি বসানো)
    text = text.replace("whatsapp", "WhatsApp 💬").replace("facebook", "Facebook 🟦").replace("otp", "OTP 🔐")
    
    # লাইন ভাঙার লজিক (প্রতি ৬-৭ শব্দ পর পর লাইন ভাঙবে)
    words = text.split()
    lines = []
    for i in range(0, len(words), 7):
        lines.append(" ".join(words[i:i+7]))
    
    formatted_text = "\n".join(lines)
    return f"<blockquote>{formatted_text}</blockquote>"

async def ask_broadcast(c: types.CallbackQuery):
    await c.message.answer("<b>Send your message (Bot will auto-format it):</b>", parse_mode='HTML')
    await AdminStates.waiting_for_broadcast.set()

async def send_broadcast(m: types.Message, state: FSMContext):
    users = await db.get_all_users()
    
    # বটের স্মার্ট ব্রেইন ইউজ করে টেক্সট সাজানো
    final_text = smart_formatter(m.text) if m.text else m.caption
    
    # অ্যাডমিনের সেট করা ব্রডকাস্ট বাটন
    dyn_btns = await db.get_dynamic_buttons("broadcast")
    markup = inline_kb.otp_success_keyboard(dyn_btns) if dyn_btns else None

    count = 0
    for u in users:
        try:
            if m.text:
                await m.bot.send_message(u['user_id'], final_text, parse_mode='HTML', reply_markup=markup)
            else:
                await m.copy_to(u['user_id'], reply_markup=markup)
            count += 1
        except: pass
        
    await m.answer(f"📢 <b>Broadcast Complete!</b> Sent to {count} users.", parse_mode='HTML')
    await state.finish()

# --- NEW: Detailed Stats ---
async def stats(c: types.CallbackQuery):
    t_users, a_users, w_otp, s_otp = await db.get_detailed_stats()
    text = f"""
📊 <b><u>Detailed System Stats:</u></b>

👥 <b>Total Users:</b> {t_users}
🟢 <b>Active (24h):</b> {a_users}
⏳ <b>Waiting for OTP:</b> {w_otp}
✅ <b>Total OTPs Delivered:</b> {s_otp}
"""
    await c.message.answer(text, parse_mode='HTML')

# --- NEW: Member List Downloader (The Hacker Way) ---
async def download_members(c: types.CallbackQuery):
    await c.answer("Generating Member List... Please wait ⏳")
    users = await db.get_all_users()
    
    file_content = "ID | Name | Username | Last Active\n"
    file_content += "-"*50 + "\n"
    
    for u in users:
        file_content += f"{u['user_id']} | {u.get('name', 'N/A')} | @{u.get('username', 'N/A')} | {u.get('last_active', 'N/A')}\n"
        
    file = io.BytesIO(file_content.encode('utf-8'))
    file.name = "Member_List.txt"
    
    await c.bot.send_document(chat_id=config.ADMIN_ID, document=file, caption="📁 <b>Here is your detailed Member List!</b>", parse_mode='HTML')

def register_admin_handlers(dp: Dispatcher):
    dp.register_callback_query_handler(ask_broadcast, lambda c: c.data == 'admin_broadcast')
    dp.register_message_handler(send_broadcast, state=AdminStates.waiting_for_broadcast, content_types=types.ContentTypes.ANY, chat_type=types.ChatType.PRIVATE)
    dp.register_callback_query_handler(stats, lambda c: c.data == 'admin_stats')
    dp.register_callback_query_handler(download_members, lambda c: c.data == 'admin_members')