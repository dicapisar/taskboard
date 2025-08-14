from redis.asyncio import Redis
from src.app.core.config import settings

# Initialize Redis connection
redis = Redis.from_url(settings.REDIS_URL, decode_responses=True)

async def get_redis() -> Redis:
    """
    Dependency to get the Redis instance.
    """
    return redis