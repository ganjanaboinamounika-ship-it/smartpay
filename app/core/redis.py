import redis

from app.core.config import settings


redis_client = redis.Redis.from_url(
    settings.REDIS_URL,
    decode_responses=True,
)


def get_redis():
    return redis_client


def check_redis_connection() -> bool:
    try:
        return redis_client.ping()
    except redis.RedisError:
        return False