MAX_CONCURRENT_REQUESTS = 400  # 10,000 ইউজারের জন্য 400 এর লিমিট
current_requests = 0

def is_overloaded():
    global current_requests
    return current_requests >= MAX_CONCURRENT_REQUESTS

async def add_req():
    global current_requests
    current_requests += 1

async def remove_req():
    global current_requests
    current_requests -= 1
    if current_requests < 0:
        current_requests = 0