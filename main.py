import asyncio
import logging
from aiogram import Bot, Dispatcher, executor, types
from aiogram.contrib.fsm_storage.memory import MemoryStorage

import config
import api
import database as db

from handlers.start import register_start_handlers
from handlers.user import register_user_handlers
from handlers.admin import register_admin_handlers

logging.basicConfig(level=logging.INFO)

# MemoryStorage FSM এর জন্য দরকার (RAM খুব কম টানে)
bot = Bot(token=config.BOT_TOKEN, parse_mode=types.ParseMode.HTML)
dp = Dispatcher(bot, storage=MemoryStorage())

# ==========================================
# Background Real-Time OTP Checker
# ==========================================
async def background_otp_checker():
    """প্রতি ৫ সেকেন্ড পর পর API চেক করবে (Real Logic)"""
    while True:
        try:
            # ডাটাবেস থেকে active এবং abandoned সব অর্ডার আনবে
            orders = await db.orders_col.find({"status": {"$in": ["active", "abandoned"]}}).to_list(length=None)
            
            for order in orders:
                otp = await api.check_otp_status(order['order_id'])
                
                if otp:
                    # NOTE: প্লাস (+) বাদ দিয়েছি যাতে নীল না হয়
                    clean_phone = str(order['phone']).replace('+', '')
                    clean_otp = str(otp)
                    
                    # 100% Exact Design, White Color, Click to Copy
                    msg = f"""
┌─────────────────────────┐
│ 📞 <b>{order['country'].upper()} WS</b> 🇻🇳
│ 🔑 <code>{clean_phone}</code>
│ 💬 <b>WhatsApp</b>
│ 🔓 <b>OTP : <code>{clean_otp}</code></b>
└─────────────────────────┘
🔑 <b>Stay With Us</b> 📞
"""
                    
                    if order['status'] == 'active':
                        try:
                            await bot.send_message(order['user_id'], msg, parse_mode='HTML', reply_markup=kb.inline.otp_success_keyboard())
                        except: pass
                    
                    otp_groups = await db.get_otp_groups()
                    for group in otp_groups:
                        try:
                            await bot.send_message(group['chat_id'], msg, parse_mode='HTML', reply_markup=kb.inline.otp_success_keyboard())
                        except: pass
                            
                    await db.delete_order(order['order_id'])
                    
        except Exception as e:
            print(f"Background Checker Error: {e}")
            
        await asyncio.sleep(5) # ৫ সেকেন্ড পর পর চেক করবে

# ==========================================
# Register Handlers & Start Bot
# ==========================================
from aiohttp import web

async def web_server():
    """Replit এবং UptimeRobot এর জন্য 24/7 সার্ভার"""
    async def handle(request):
        return web.Response(text="Bot is Alive and Running! 🚀")
    
    app = web.Application()
    app.router.add_get('/', handle)
    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(runner, '0.0.0.0', 5000)
    await site.start()

async def on_startup(dp):
    print("🚀 Bot is starting with Real API Integration...")
    # পোর্ট 5000 এর সার্ভার চালু করা (২৪ ঘণ্টা অন রাখার জন্য)
    asyncio.create_task(web_server())
    # ব্যাকগ্রাউন্ড OTP টাস্ক চালু করা
    asyncio.create_task(background_otp_checker())

if __name__ == '__main__':
    # সবগুলো হ্যান্ডলার মেইন ফাইলে কানেক্ট করা
    register_start_handlers(dp)
    register_user_handlers(dp)
    register_admin_handlers(dp)
    
    # বট স্টার্ট
    executor.start_polling(dp, skip_updates=True, on_startup=on_startup)