MAX_CONCURRENT_REQUESTS = 400  # 400 জনের লিমিট
current_requests = 0

def get_wait_time():
    """সার্ভারে লোড পড়লে সিরিয়াল অনুযায়ী ওয়েট টাইম দিবে"""
    global current_requests
    if current_requests >= MAX_CONCURRENT_REQUESTS:
        extra_load = current_requests - MAX_CONCURRENT_REQUESTS
        if extra_load < 50:
            return 1 # Wait 1 second
        elif extra_load < 150:
            return 2 # Wait 2 seconds
        else:
            return 3 # Wait 3 seconds
    return 0

async def add_req():
    global current_requests
    current_requests += 1

async def remove_req():
    global current_requests
    current_requests -= 1
    if current_requests < 0:
        current_requests = 0