import os
import asyncio
from aiogram import Bot, Dispatcher, types
from aiohttp import web

TOKEN = os.getenv("BOT_TOKEN")

bot = Bot(token=TOKEN)
dp = Dispatcher(bot)

@dp.message_handler(commands=['start'])
async def start(msg: types.Message):
    await msg.reply("Bot is working ✅")

# web server for render
async def web_server():
    async def handler(request):
        return web.Response(text="Bot Alive")

    app = web.Application()
    app.router.add_get("/", handler)

    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(runner, "0.0.0.0", 10000)
    await site.start()

async def main():
    await web_server()
    await dp.start_polling()

if __name__ == "__main__":
    asyncio.run(main())
