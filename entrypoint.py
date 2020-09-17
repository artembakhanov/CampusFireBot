import redis
from env import *

while True:
    try:
        db = redis.Redis(host=REDIS_URL, port=REDIS_PORT)
        break
    except:
        print("Redis is not available")
print("Redis is available now! Starting the bot...")
