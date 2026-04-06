# --- TESTING api.py (ডেমো চেক করার জন্য) ---
import asyncio
import random

async def get_countries():
    """আপনাকে চেক করার জন্য কিছু ডেমো কান্ট্রি দেখাবে"""
    # একটু ওয়েট করার ফিল দেওয়ার জন্য
    await asyncio.sleep(0.5) 
    return [
        ("🇧🇩 Bangladesh WS", 150, "bd"),
        ("🇺🇸 USA Telegram", 85, "us"),
        ("🇿🇲 Zambia WS+FB", 400, "zm"),
        ("🇸🇩 Sudan WS", 12, "sd")
    ]

async def buy_number(country_code):
    """ক্লিক করলে ফেক রেন্ডম নাম্বার জেনারেট করে দিবে"""
    await asyncio.sleep(1) # API থেকে নাম্বার আসার ফিল
    
    order_id = str(random.randint(100000, 999999))
    
    # দেশের কোড অনুযায়ী ডেমো নাম্বার
    if country_code == 'bd':
        phone = f"88017{random.randint(10000000, 99999999)}"
    elif country_code == 'us':
        phone = f"1{random.randint(2000000000, 9999999999)}"
    else:
        phone = f"249{random.randint(100000000, 999999999)}"
        
    return {"order_id": order_id, "phone": phone}

async def check_otp_status(order_id):
    """ব্যাকগ্রাউন্ড চেকার বা View OTP তে চাপ দিলে ফেক OTP দিবে"""
    # এখানে লজিক হলো: প্রতিবার চেক করার সময় ২০% চান্স থাকবে OTP আসার।
    # এতে করে আপনি বুঝতে পারবেন যে ব্যাকগ্রাউন্ড চেকার অটোমেটিক কাজ করছে!
    if random.random() < 0.20:
        return str(random.randint(1000, 9999))
    return None

async def cancel_number(order_id):
    """নাম্বার ক্যানসেলের ফেক লজিক"""
    return True