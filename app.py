import asyncio
from aiohttp import web
from main import dp, bot, on_startup

# --- ফেক ওয়েব সার্ভার (পিং খাওয়ার জন্য) ---
async def handle_ping(request):
    return web.Response(text="Bot is ALIVE and running! Mady by Hacker Mindset.")

async def start_web_server():
    app = web.Application()
    app.router.add_get('/', handle_ping)
    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(runner, '0.0.0.0', 7860) # Hugging Face/Render Port
    await site.start()
    print("Fake Web Server started on port 7860!")

async def main():
    # ওয়েব সার্ভার চালু করবে
    await start_web_server()
    
    # টেলিগ্রাম বট চালু করবে
    await on_startup(dp)
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())