from aiogram import types, Dispatcher
from aiogram.dispatcher.filters import Text
import database as db
import keyboards.reply as reply_kb
import keyboards.inline as inline_kb

async def check_membership(bot, user_id):
    fj_channels = await db.get_fj_channels()
    fj_groups = await db.get_fj_groups()
    for ch in fj_channels + fj_groups:
        try:
            member = await bot.get_chat_member(chat_id=ch['chat_id'], user_id=user_id)
            if member.status in ['left', 'kicked', 'restricted']: return False
        except: return False
    return True

async def cmd_start(message: types.Message):
    user_id = message.from_user.id
    await db.add_user(user_id)
    
    fj_channels = await db.get_fj_channels()
    fj_groups = await db.get_fj_groups()
    
    if fj_channels or fj_groups:
        is_joined = await check_membership(message.bot, user_id)
        if not is_joined:
            text = "আসসালামু আলাইকুম বটে আপনাকে স্বাগতম। 😍😇\nবট ব্যবহার করার জন্য নিচে দেওয়া চ্যানেলগুলোতে জয়েন হয়ে ভেরিফাই করুন। 💖"
            await message.answer(text, reply_markup=inline_kb.force_join_keyboard(fj_channels, fj_groups))
            return

    await message.answer("Welcome! Choose your option:", reply_markup=reply_kb.main_menu(user_id))

async def verify_join_btn(callback_query: types.CallbackQuery):
    user_id = callback_query.from_user.id
    if await check_membership(callback_query.bot, user_id):
        await callback_query.message.delete()
        await callback_query.message.answer("✅ <b>Verification Successful! Welcome!</b>", parse_mode='HTML', reply_markup=reply_kb.main_menu(user_id))
    else:
        await callback_query.answer("❌ আপনি এখনও সবগুলোতে জয়েন হননি!", show_alert=True)

def register_start_handlers(dp: Dispatcher):
    dp.register_message_handler(cmd_start, commands=['start'], chat_type=types.ChatType.PRIVATE)