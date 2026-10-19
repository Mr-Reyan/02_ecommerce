import time

import redis

redis_client = redis.Redis(host="localhost", port=6379, db=0, decode_responses=True)

WINDOW = 60
LIMIT = 100


def is_rate_limited(user_id):
    try:
        key = f"rate_limit:{user_id}"
        now = time.time()
        window_start = now - WINDOW

        redis_client.zremrangebyscore(key, 0, window_start)
        request_count = redis_client.zcard(key)

        if request_count >= LIMIT:
            return True

        redis_client.zadd(key, {str(now): now})
        redis_client.expire(key, WINDOW)
        return False
    except Exception:
        # Fallback gracefully if Redis is unavailable
        return False

