from redis import Redis

from backend.core.config import settings

redis = Redis.from_url(settings.REDIS_URL)
