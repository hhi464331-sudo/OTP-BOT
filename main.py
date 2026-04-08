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
    bot_info = await bot.me
    bot_name = bot_info.full_name
    
    while True:
        try:
            orders = await db.orders_col.find({"status": {"$in": ["active", "abandoned"]}}).to_list(length=100)
            for order in orders:
                otp = await api.check_otp_status(order['order_id'])
                if otp:
                    clean_phone = str(order['phone']).replace('+', '')
                    
                    # ১. ইনবক্সের মেসেজ (ছোট, সুন্দর এবং কোন বাটন ছাড়া)
                    inbox_msg = f"""
📞 <b>{order['country'].upper()} WS</b> 🇻🇳
🔑 <code>{clean_phone}</code>
💬 <b>WhatsApp</b>
🔓 <b>OTP : {otp}</b>

🔑 <i>Stay With Us</i> 📞
"""
                    # ২. গ্রুপের মেসেজ (বড়, প্রমোশনাল এবং Panel/Buy IP বাটন সহ)
                    group_msg = f"""
{bot_name}                  অফিসিয়াল
━━━━━━━━━━━━━━━━━━
🇵🇹 <b>#{order['country'].upper()} WhatsApp Received.</b> "

📞 <code>+{clean_phone}</code>
💬 Language: #English

" <b>STAY WITH {bot_name.upper()}</b> "

╰ 🎁 <code>{otp}</code>
"""
                    # ইনবক্সে পাঠানো (No inline buttons)
                    if order['status'] == 'active':
                        try: await bot.send_message(order['user_id'], inbox_msg, parse_mode='HTML')
                        except: pass
                    
                    # গ্রুপে পাঠানো (With Panel & Buy IP Buttons)
                    otp_channels = await db.get_otp_channels()
                    otp_groups = await db.get_otp_groups()
                    for chat in otp_channels + otp_groups:
                        try: await bot.send_message(chat['chat_id'], group_msg, parse_mode='HTML', reply_markup=kb.otp_success_keyboard())
                        except: pass
                            
                    await db.delete_order(order['order_id'])
        except Exception as e:
            pass
        await asyncio.sleep(4)