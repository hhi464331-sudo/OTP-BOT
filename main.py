import asyncio
import logging
from aiogram import Bot, Dispatcher, executor, types
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiohttp import web

import config
import api
import database as db
import keyboards.inline as kb

from handlers.start import register_start_handlers
from handlers.user import register_user_handlers
from handlers.admin import register_admin_handlers

logging.basicConfig(level=logging.INFO)

bot = Bot(token=config.BOT_TOKEN, parse_mode=types.ParseMode.HTML)
dp = Dispatcher(bot, storage=MemoryStorage())

# ==========================================
# Background Real-Time OTP Checker
# ==========================================
async def background_otp_checker():
    """প্রতি ৪ সেকেন্ড পর পর API চেক করবে (Real Logic)"""
    while True:
        try:
            orders = await db.orders_col.find({"status": {"$in": ["active", "abandoned"]}}).to_list(length=100)
            
            for order in orders:
                otp = await api.check_otp_status(order['order_id'])
                
                if otp:
                    clean_phone = str(order['phone']).replace('+', '')
                    
                    # 100% Exact Video Design
                    msg = f"""
OTP ZONE                  ছোট মিয়া
━━━━━━━━━━━━━━━━━━
🇵🇹 <b>#{order['country'].upper()} WhatsApp Received.</b> "

📞 <code>+{clean_phone}</code>
💬 Language: #English

" <b>STAY WITH SMS ZONE</b> "

╰ 🎁 <code>{otp}</code>
"""
                    
                    if order['status'] == 'active':
                        try:
                            await bot.send_message(order['user_id'], msg, reply_markup=kb.otp_success_keyboard())
                        except: pass
                    
                    otp_groups = await db.get_otp_groups()
                    for group in otp_groups:
                        try:
                            await bot.send_message(group['chat_id'], msg, reply_markup=kb.otp_success_keyboard())
                        except: pass
                            
                    await db.delete_order(order['order_id'])
                    
        except Exception as e:
            pass
            
        await asyncio.sleep(4) 

# ==========================================
# 24/7 Keep Alive Server
# ==========================================
async def handle(request):
    return web.Response(text="Bot is Alive and Running! 🚀")

async def web_server():
    app = web.Application()
    app.router.add_get('/', handle)
    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(runner, '0.0.0.0', 5000)
    await site.start()

async def on_startup(dp):
    print("🚀 Bot is starting...")
    asyncio.create_task(web_server())
    asyncio.create_task(background_otp_checker())

if __name__ == '__main__':
    register_start_handlers(dp)
    register_user_handlers(dp)
    register_admin_handlers(dp)
    
    executor.start_polling(dp, skip_updates=True, on_startup=on_startup)