from redis.asyncio import Redis
from src.app.core.config import settings

# crea instancia de Redis asyncio
redis = Redis.from_url(settings.REDIS_URL, decode_responses=True)