# Import Redis support for asynchronous operations
from redis.asyncio import Redis

# Import application settings containing the Redis connection URL
from src.app.core.config import settings

# ---------------------------- Redis Client Initialization ----------------------------

# Initialize a global Redis client using the connection URL from settings.
# The parameter decode_responses=True ensures that Redis responses are returned as strings instead of bytes.
redis = Redis.from_url(settings.REDIS_URL, decode_responses=True)

# ---------------------------- Dependency Injection ----------------------------

async def get_redis() -> Redis:
    """
    This function is used as a dependency to provide the Redis instance.
    It allows FastAPI to inject the Redis connection wherever it is needed.
    """
    return redis