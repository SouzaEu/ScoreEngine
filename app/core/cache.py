from fastapi_cache import FastAPICache
from fastapi_cache.backends.redis import RedisBackend
from fastapi_cache.decorator import cache
from redis import asyncio as aioredis
from app.core.config import settings

async def init_cache():
    """
    Inicializa o cache Redis
    """
    redis = aioredis.from_url(
        f"redis://{settings.REDIS_HOST}:{settings.REDIS_PORT}",
        encoding="utf8",
        decode_responses=True
    )
    FastAPICache.init(RedisBackend(redis), prefix="score_engine")

# Decorator personalizado para cache de scores
def cache_score(expire: int = 3600):
    """
    Cache de scores com expiração padrão de 1 hora
    """
    return cache(
        expire=expire,
        namespace="scores",
        key_builder=lambda *args, **kwargs: f"score:{kwargs.get('user_id')}"
    )

# Decorator personalizado para cache de features
def cache_features(expire: int = 1800):
    """
    Cache de features com expiração padrão de 30 minutos
    """
    return cache(
        expire=expire,
        namespace="features",
        key_builder=lambda *args, **kwargs: f"features:{kwargs.get('user_id')}"
    ) 