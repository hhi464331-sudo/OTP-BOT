from motor.motor_asyncio import AsyncIOMotorClient
import config

client = AsyncIOMotorClient(config.MONGO_URI)
db = client['sms_zone_db']

users_col = db['users']
channels_col = db['channels']
otp_channels_col = db['otp_channels']
orders_col = db['orders']

async def add_user(user_id):
    await users_col.update_one({"user_id": user_id}, {"$set": {"user_id": user_id}}, upsert=True)

async def get_all_users():
    return await users_col.find({}).to_list(length=None)

# Force Join
async def add_channel(chat_id, link, name):
    await channels_col.insert_one({"chat_id": chat_id, "link": link, "name": name})

async def get_channels():
    return await channels_col.find({}).to_list(length=None)

async def remove_channel(chat_id):
    await channels_col.delete_one({"chat_id": chat_id})

# OTP Groups
async def add_otp_group(chat_id):
    await otp_channels_col.insert_one({"chat_id": chat_id})

async def get_otp_groups():
    return await otp_channels_col.find({}).to_list(length=None)

# Order Logic (যেটা ব্যাকগ্রাউন্ড টাস্কে কাজ করবে)
async def save_order(user_id, order_id, phone, country):
    await orders_col.insert_one({
        "user_id": user_id,
        "order_id": order_id,
        "phone": phone,
        "country": country,
        "status": "active"
    })

async def get_pending_orders():
    return await orders_col.find({"status": "active"}).to_list(length=None)

async def delete_order(order_id):
    await orders_col.delete_one({"order_id": order_id})