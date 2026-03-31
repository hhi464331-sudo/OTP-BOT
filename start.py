from aiogram import types, Dispatcher
from aiogram.dispatcher.filters import Text
import database as db
import keyboards.reply as reply_kb
import keyboards.inline as inline_kb

async def check_membership(bot, user_id, channels):
    """টেলিগ্রামের আসল API দিয়ে চেক করবে ইউজার চ্যানেলে জয়েন আছে কি না"""
    for ch in channels:
        try:
            member = await bot.get_chat_member(chat_id=ch['chat_id'], user_id=user_id)
            if member.status in ['left', 'kicked', 'restricted']:
                return False
        except Exception as e:
            # যদি বট ওই চ্যানেলে অ্যাডমিন না থাকে, তাহলে চেক করতে পারবে না
            print(f"Membership check error for {ch['chat_id']}: {e}")
            return False
    return True

async def cmd_start(message: types.Message):
    """/start কমান্ডের রিয়েল লজিক"""
    user_id = message.from_user.id
    await db.add_user(user_id) # ডাটাবেসে সেভ
    
    channels = await db.get_channels()
    
    if channels:
        bot = message.bot
        is_joined = await check_membership(bot, user_id, channels)
        
        if not is_joined:
            text = (
                "আসসালামু আলাইকুম SMS ZONE বটে আপনাকে স্বাগতম। 😍😇\n"
                "বট ব্যবহার করার জন্য নিচে দেওয়া চ্যানেলগুলোতে জয়েন হয়ে ভেরিফাই করুন। 💖"
            )
            await message.answer(text, reply_markup=inline_kb.force_join_keyboard(channels))
            return

    # যদি চ্যানেল না থাকে বা জয়েন করা থাকে
    await message.answer("Welcome! Choose your option:", reply_markup=reply_kb.main_menu())

async def verify_join(callback_query: types.CallbackQuery):
    """Verify বাটনে চাপ দিলে চেক করার রিয়েল লজিক"""
    user_id = callback_query.from_user.id
    channels = await db.get_channels()
    bot = callback_query.bot
    
    is_joined = await check_membership(bot, user_id, channels)
    
    if is_joined:
        await callback_query.message.delete()
        await callback_query.message.answer("✅ Verification Successful! Welcome!", reply_markup=reply_kb.main_menu())
    else:
        await callback_query.answer("❌ আপনি এখনও সব চ্যানেলে জয়েন হননি। দয়া করে জয়েন করুন।", show_alert=True)

def register_start_handlers(dp: Dispatcher):
    """মেইন ফাইলে কল করার জন্য ফাংশন রেজিস্টার"""
    dp.register_message_handler(cmd_start, commands=['start'])
    dp.register_callback_query_handler(verify_join, Text(equals="verify_join"))