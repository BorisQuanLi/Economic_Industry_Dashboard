"""Redis cache — circuit breaker fallback for Firestore lookups.
Ported from fastapi_backend/cache.py; same graceful-degradation pattern used
by the Airflow FMP pipeline to absorb vendor rate limits across 500 tickers.
"""
import json
import os
import logging
from typing import Optional

import redis

logger = logging.getLogger(__name__)

REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379/0")
CACHE_TTL = int(os.getenv("CACHE_TTL_SECONDS", "300"))

_client: Optional[redis.Redis] = None


def get_redis() -> Optional[redis.Redis]:
    global _client
    if _client is None:
        try:
            _client = redis.from_url(REDIS_URL, decode_responses=True)
            _client.ping()
        except Exception as e:
            logger.warning(f"Redis unavailable, caching disabled: {e}")
            _client = None
    return _client


def cache_get(key: str) -> Optional[dict]:
    r = get_redis()
    if r is None:
        return None
    try:
        value = r.get(key)
        return json.loads(value) if value else None
    except Exception as e:
        logger.warning(f"Cache GET failed for {key}: {e}")
        return None


def cache_set(key: str, value: dict, ttl: int = CACHE_TTL) -> None:
    r = get_redis()
    if r is None:
        return
    try:
        r.setex(key, ttl, json.dumps(value))
    except Exception as e:
        logger.warning(f"Cache SET failed for {key}: {e}")
