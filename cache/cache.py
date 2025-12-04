import logging

from cache.memory_cache import MemoryCache
from cache.redis_cache import RedisCache

from config_data.config import ConfigSettings


logger = logging.getLogger(__name__)


async def create_cache(config: ConfigSettings):
    logger.info(f"Initializing cache, config: host={config.redis.host}, port={config.redis.port}")

    try:
        cache = RedisCache(
            host=config.redis.host,
            port=config.redis.port,
            db=config.redis.db,
            password=config.redis.password,
            ttl=config.redis.ttl,
        )
        await cache.redis.ping()
        logger.info("RedisCache initialized successfully")
        return cache

    except Exception as e:
        logger.error(f"Redis unavailable, switching to MemoryCache: {e}")
        return MemoryCache()
