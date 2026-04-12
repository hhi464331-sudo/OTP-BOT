from motor.motor_asyncio import AsyncIOMotorClient
import config
from datetime import datetime, timedelta

client = AsyncIOMotorClient(config.MONGO_URI)
db = client['sms_zone_db']

users_col = db['users']
orders_col = db['orders']
settings_col = db['settings']

# Force Join & OTP Sources
fj_channels_col = db['fj_channels']
fj_groups_col = db['fj_groups']
otp_channels_col = db['otp_channels']
otp_groups_col = db['otp_groups']

# New: Dynamic Buttons & Emoji Brain
dyn_buttons_col = db['dynamic_buttons']
emoji_map_col = db['emoji_mapping']
spam_tracker_col = db['spam_tracker'] # For 2-second delay

# --- USER SYSTEM (Hacker Mindset) ---
async def add_user(user_id, full_name, username):
    """ইউজারের সব ডাটা সেভ করবে মেম্বার লিস্টের জন্য"""
    user_data = {
        "user_id": user_id,
        "name": full_name,
        "username": username if username else "Hidden",
        "last_active": datetime.now()
    }
    await users_col.update_one({"user_id": user_id}, {"$set": user_data}, upsert=True)

async def get_all_users():
    return await users_col.find({}).to_list(length=None)

# --- DETAILED STATS ---
async def get_detailed_stats():
    total_users = await users_col.count_documents({})
    
    # গত ২৪ ঘণ্টায় কতজন একটিভ ছিল
    yesterday = datetime.now() - timedelta(days=1)
    active_24h = await users_col.count_documents({"last_active": {"$gte": yesterday}})
    
    waiting_otp = await orders_col.count_documents({"status": "active"})
    success_otp = await settings_col.find_one({"_id": "success_count"})
    success_count = success_otp.get("count", 0) if success_otp else 0
    
    return total_users, active_24h, waiting_otp, success_count

async def increment_success_otp():
    await settings_col.update_one({"_id": "success_count"}, {"$inc": {"count": 1}}, upsert=True)

# --- ANTI-SPAM (2 Seconds Delay) ---
async def check_spam(user_id):
    """২ সেকেন্ডের ভেতরে ক্লিক করলে ব্লক করবে"""
    now = datetime.now()
    user_log = await spam_tracker_col.find_one({"user_id": user_id})
    
    if user_log:
        last_click = user_log['last_click']
        if (now - last_click).total_seconds() < 2:
            return True # Spammer detected
            
    await spam_tracker_col.update_one({"user_id": user_id}, {"$set": {"last_click": now}}, upsert=True)
    return False

# --- DYNAMIC BUTTONS & BRAIN ---
async def add_dynamic_button(btn_type, name, link):
    # btn_type = 'otp', 'main_menu', 'broadcast'
    await dyn_buttons_col.insert_one({"type": btn_type, "name": name, "link": link})

async def get_dynamic_buttons(btn_type):
    return await dyn_buttons_col.find({"type": btn_type}).to_list(length=None)

async def remove_dynamic_button(btn_id):
    from bson.objectid import ObjectId
    await dyn_buttons_col.delete_one({"_id": ObjectId(btn_id)})

# --- ORDER & GARBAGE COLLECTION ---
async def save_order(user_id, order_id, phone, country):
    await orders_col.insert_one({"user_id": user_id, "order_id": order_id, "phone": phone, "country": country, "status": "active"})

async def update_order_status(order_id, status):
    """ইউজার ক্যানসেল করলে ডাটাবেসে status abandoned হবে, ডিলিট হবে না"""
    await orders_col.update_one({"order_id": order_id}, {"$set": {"status": status}})

async def delete_order(order_id):
    """OTP আসার ৫ সেকেন্ড পর ডাটাবেস থেকে পার্মানেন্ট ক্লিয়ার (Garbage Collection)"""
    await orders_col.delete_one({"order_id": order_id})

# --- CHANNEL/GROUP FETCHERS ---
async def get_fj_channels(): return await fj_channels_col.find({}).to_list(length=None)
async def get_fj_groups(): return await fj_groups_col.find({}).to_list(length=None)
async def get_otp_channels(): return await otp_channels_col.find({}).to_list(length=None)
async def get_otp_groups(): return await otp_groups_col.find({}).to_list(length=None)

# System Power
async def is_system_online():
    setting = await settings_col.find_one({"_id": "power"})
    return setting.get("status", True) if setting else True