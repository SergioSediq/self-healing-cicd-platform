"""Redis-backed cache for analysis. Falls back to file cache when REDIS_URL unset."""
import json
import os

from .cache import get_cached_analysis as _file_get, set_cached_analysis as _file_set, _log_hash


def get_cached_analysis(logs: str) -> dict | None:
    if os.getenv("CACHE_DISABLED", "").lower() in ("1", "true", "yes"):
        return None
    try:
        import redis
        url = os.getenv("REDIS_URL")
        if url:
            r = redis.from_url(url)
            key = f"heal:analysis:{_log_hash(logs)}"
            raw = r.get(key)
            return json.loads(raw) if raw else None
    except (ImportError, Exception):
        pass
    return _file_get(logs)


def set_cached_analysis(logs: str, analysis: dict, ttl: int = 86400) -> None:
    if os.getenv("CACHE_DISABLED", "").lower() in ("1", "true", "yes"):
        return
    try:
        import redis
        url = os.getenv("REDIS_URL")
        if url:
            r = redis.from_url(url)
            key = f"heal:analysis:{_log_hash(logs)}"
            r.setex(key, ttl, json.dumps(analysis))
            return
    except (ImportError, Exception):
        pass
    _file_set(logs, analysis)
