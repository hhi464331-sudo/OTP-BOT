import os
from aiogram import Bot, Dispatcher, types, executor
from aiohttp import web

TOKEN = os.getenv("BOT_TOKEN")

bot = Bot(token=TOKEN)
dp = Dispatcher(bot)

# ================= BOT =================

@dp.message_handler(commands=['start'])
async def start(msg: types.Message):
    await msg.reply("Bot is working ✅")

# ================= WEB SERVER =================

async def handle(request):
    return web.Response(text="Bot Alive")

async def start_web():
    app = web.Application()
    app.router.add_get("/", handle)

    PORT = int(os.environ.get("PORT", 10000))

runner = web.AppRunner(app)
await runner.setup()

site = web.TCPSite(runner, "0.0.0.0", PORT)
await site.start()

# ================= MAIN =================

if __name__ == "__main__":
    import asyncio
    loop = asyncio.get_event_loop()
    loop.create_task(start_web())
    executor.start_polling(dp, skip_updates=True)
