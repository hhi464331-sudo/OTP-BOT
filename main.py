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
    """OTP ચેক করে গ্রুপ এবং ইনবক্সে পাঠানোর সিস্টেম"""
    # বটের আসল নাম বের করে নিচ্ছি (যেমন: Virtual Number Hub)
    bot_info = await bot.me
    bot_name = bot_info.full_name
    
    while True:
        try:
            orders = await db.orders_col.find({"status": {"$in": ["active", "abandoned"]}}).to_list(length=100)
            
            for order in orders:
                otp = await api.check_otp_status(order['order_id'])
                
                if otp:
                    clean_phone = str(order['phone']).replace('+', '')
                    
                    # 100% Dynamic Message Design (কোনো ছোট মিয়া বা SMS ZONE নেই)
                    msg = f"""
{bot_name}                  অফিসিয়াল
━━━━━━━━━━━━━━━━━━
🇵🇹 <b>#{order['country'].upper()} WhatsApp Received.</b> "

📞 <code>+{clean_phone}</code>
💬 Language: #English

" <b>STAY WITH {bot_name.upper()}</b> "

╰ 🎁 <code>{otp}</code>
"""
                    # ইনবক্সে পাঠানো
                    if order['status'] == 'active':
                        try:
                            await bot.send_message(order['user_id'], msg, parse_mode='HTML', reply_markup=kb.otp_success_keyboard())
                        except: pass
                    
                    # OTP চ্যানেল এবং গ্রুপে পাঠানো
                    otp_channels = await db.get_otp_channels()
                    otp_groups = await db.get_otp_groups()
                    
                    for chat in otp_channels + otp_groups:
                        try:
                            await bot.send_message(chat['chat_id'], msg, parse_mode='HTML', reply_markup=kb.otp_success_keyboard())
                        except: pass
                            
                    # OTP পাওয়ার পর ডাটাবেস থেকে ডিলিট
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
    print(f"🚀 Bot is starting...")
    asyncio.create_task(web_server())
    asyncio.create_task(background_otp_checker())

if __name__ == '__main__':
    register_start_handlers(dp)
    register_user_handlers(dp)
    register_admin_handlers(dp)
    
    executor.start_polling(dp, skip_updates=True, on_startup=on_startup)