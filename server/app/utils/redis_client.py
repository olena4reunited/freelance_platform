import redis


redis_client = redis.Redis(host='localhost', port=6379, decode_responses=True)

redis_reset_passwd = redis.Redis(host='localhost', port=6379, db=1, decode_responses=True)
