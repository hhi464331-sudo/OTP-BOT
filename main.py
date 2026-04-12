import asyncio
import logging
from aiogram import Bot, Dispatcher, executor, types
from aiogram.contrib.fsm_storage.memory import MemoryStorage
import config
import api
import database as db
import keyboards.inline as inline_kb

from handlers.start import register_start_handlers
from handlers.user import register_user_handlers
from handlers.admin import register_admin_handlers

logging.basicConfig(level=logging.INFO)
bot = Bot(token=config.BOT_TOKEN, parse_mode=types.ParseMode.HTML)
dp = Dispatcher(bot, storage=MemoryStorage()) # Not a big issue for 10k since we clear orders fast now!

# ==========================================
# Background Real-Time OTP Checker
# ==========================================
async def background_otp_checker():
    while True:
        try:
            # Active এবং Abandoned (বাতিল করা) দুটোর জন্যই চেক করবে
            orders = await db.orders_col.find({"status": {"$in": ["active", "abandoned"]}}).to_list(length=100)
            
            for order in orders:
                otp = await api.check_otp_status(order['order_id'])
                if otp:
                    clean_phone = str(order['phone']).replace('+', '')
                    country = order['country'].upper()
                    
                    # --- NEW GORGEOUS OTP DESIGN (Screenshot 4 Style) ---
                    msg_text = f"""
✅ 🇻🇳 <b>{country} WhatsApp Otp Code Received Successfully</b> 🎉

🔓 <b>Your OTP:</b> <code>{otp}</code>

☎️ <b>Number:</b> {clean_phone}
⚙️ <b>Service:</b> WhatsApp
🌍 <b>Country:</b> {country}

📥 <b>Full-Message:</b>
<blockquote># Your WhatsApp Business code {otp}
Don't share this code with others</blockquote>
"""
                    # ডাটাবেস থেকে অ্যাডমিনের সেট করা বাটন আনবে
                    dyn_btns = await db.get_dynamic_buttons("otp")
                    markup = inline_kb.otp_success_keyboard(dyn_btns) if dyn_btns else None

                    # ১. ইনবক্সে পাঠানো (যদি ইউজার ক্যানসেল না করে থাকে)
                    if order['status'] == 'active':
                        try: await bot.send_message(order['user_id'], msg_text, parse_mode='HTML')
                        except: pass
                    
                    # ২. গ্রুপে পাঠানো (সবার জন্য)
                    otp_channels = await db.get_otp_channels()
                    otp_groups = await db.get_otp_groups()
                    for chat in otp_channels + otp_groups:
                        try: await bot.send_message(chat['chat_id'], msg_text, parse_mode='HTML', reply_markup=markup)
                        except: pass
                            
                    await db.increment_success_otp()
                    
                    # --- THE GARBAGE COLLECTION ---
                    # ৫ সেকেন্ড ওয়েট করে ডাটাবেস থেকে ডিলিট করে দিবে, র‍্যাম একদম ফ্রি!
                    await asyncio.sleep(5) 
                    await db.delete_order(order['order_id'])
                    
        except Exception as e:
            logging.error(f"OTP Checker Error: {e}") # এখন আর সাইলেন্টলি মরবে না, লগ দেখাবে
            
        await asyncio.sleep(3) # ৩ সেকেন্ড পর পর চেক করবে

# Register all handlers
register_start_handlers(dp)
register_user_handlers(dp)
register_admin_handlers(dp)

async def on_startup(dispatcher):
    # বটের সাথে ব্যাকগ্রাউন্ড চেকার লুপ চালু করবে
    asyncio.create_task(background_otp_checker())
    print("Bot is running perfectly!")

if __name__ == '__main__':
    # এই ফাইলটা আমরা সরাসরি রান করব না, আমরা app.py রান করব সার্ভারের জন্য
    pass