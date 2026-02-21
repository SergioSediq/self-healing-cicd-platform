"""Cache for log analysis results by content hash."""
import hashlib
import json
import os
from pathlib import Path

CACHE_DIR = Path(os.getenv("ANALYSIS_CACHE_DIR", "logs/cache"))


def _log_hash(logs: str) -> str:
    return hashlib.sha256(logs.encode("utf-8", errors="replace")).hexdigest()


def get_cached_analysis(logs: str) -> dict | None:
    """Return cached analysis if exists, else None."""
    if os.getenv("CACHE_DISABLED", "").lower() in ("1", "true", "yes"):
        return None
    key = _log_hash(logs)
    path = CACHE_DIR / f"{key}.json"
    if path.exists():
        try:
            with open(path, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            return None
    return None


def set_cached_analysis(logs: str, analysis: dict) -> None:
    """Cache analysis result."""
    if os.getenv("CACHE_DISABLED", "").lower() in ("1", "true", "yes"):
        return
    CACHE_DIR.mkdir(parents=True, exist_ok=True)
    key = _log_hash(logs)
    path = CACHE_DIR / f"{key}.json"
    with open(path, "w", encoding="utf-8") as f:
        json.dump(analysis, f)
