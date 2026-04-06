from motor.motor_asyncio import AsyncIOMotorClient
import config

client = AsyncIOMotorClient(config.MONGO_URI)
db = client['sms_zone_db']

users_col = db['users']
orders_col = db['orders']
settings_col = db['settings']

# --- SEPARATED COLLECTIONS ---
fj_channels_col = db['fj_channels']
fj_groups_col = db['fj_groups']
otp_channels_col = db['otp_channels']
otp_groups_col = db['otp_groups']

async def add_user(user_id):
    await users_col.update_one({"user_id": user_id}, {"$set": {"user_id": user_id}}, upsert=True)

async def get_all_users():
    return await users_col.find({}).to_list(length=None)

async def get_users_count():
    return await users_col.count_documents({})

async def get_active_orders_count():
    return await orders_col.count_documents({"status": "active"})

# --- 1. FORCE JOIN SYSTEM ---
async def add_fj_channel(chat_id, link, name):
    await fj_channels_col.update_one({"chat_id": chat_id}, {"$set": {"link": link, "name": name}}, upsert=True)

async def get_fj_channels():
    return await fj_channels_col.find({}).to_list(length=None)

async def remove_fj_channel(chat_id):
    await fj_channels_col.delete_one({"chat_id": chat_id})

async def add_fj_group(chat_id, link, name):
    await fj_groups_col.update_one({"chat_id": chat_id}, {"$set": {"link": link, "name": name}}, upsert=True)

async def get_fj_groups():
    return await fj_groups_col.find({}).to_list(length=None)

async def remove_fj_group(chat_id):
    await fj_groups_col.delete_one({"chat_id": chat_id})

# --- 2. OTP SYSTEM ---
async def add_otp_channel(chat_id, link, name):
    await otp_channels_col.update_one({"chat_id": chat_id}, {"$set": {"link": link, "name": name}}, upsert=True)

async def get_otp_channels():
    return await otp_channels_col.find({}).to_list(length=None)

async def remove_otp_channel(chat_id):
    await otp_channels_col.delete_one({"chat_id": chat_id})

async def add_otp_group(chat_id, link, name):
    await otp_groups_col.update_one({"chat_id": chat_id}, {"$set": {"link": link, "name": name}}, upsert=True)

async def get_otp_groups():
    return await otp_groups_col.find({}).to_list(length=None)

async def remove_otp_group(chat_id):
    await otp_groups_col.delete_one({"chat_id": chat_id})

# --- ORDER & SYSTEM LOGIC ---
async def save_order(user_id, order_id, phone, country):
    await orders_col.insert_one({"user_id": user_id, "order_id": order_id, "phone": phone, "country": country, "status": "active"})

async def delete_order(order_id):
    await orders_col.delete_one({"order_id": order_id})

async def is_system_online():
    setting = await settings_col.find_one({"_id": "power"})
    if setting: return setting.get("status", True)
    return True

async def toggle_system_power(status: bool):
    await settings_col.update_one({"_id": "power"}, {"$set": {"status": status}}, upsert=True)