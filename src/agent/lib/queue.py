"""Job queue for heal runs. Uses Redis if REDIS_URL set, else file-based."""
import json
import os
import time
import uuid
from pathlib import Path

QUEUE_DIR = Path(os.getenv("QUEUE_DIR", "logs/queue"))


def _get_redis():
    try:
        import redis
        url = os.getenv("REDIS_URL")
        if url:
            return redis.from_url(url)
    except ImportError:
        pass
    return None


def enqueue(provider: str, run_id: str, logs: str | None = None, priority: int = 0) -> str:
    """Add heal job. Returns job_id."""
    job = {"id": str(uuid.uuid4()), "provider": provider, "run_id": run_id, "logs": logs, "priority": priority, "ts": time.time()}
    r = _get_redis()
    if r:
        r.lpush("heal:queue", json.dumps(job))
        return job["id"]
    QUEUE_DIR.mkdir(parents=True, exist_ok=True)
    path = QUEUE_DIR / f"{job['id']}.json"
    with open(path, "w", encoding="utf-8") as f:
        json.dump(job, f)
    return job["id"]


def dequeue() -> dict | None:
    """Get next job. Redis: BRPOP. File: oldest by mtime."""
    r = _get_redis()
    if r:
        _, raw = r.brpop("heal:queue", timeout=1) or (None, None)
        return json.loads(raw) if raw else None
    if not QUEUE_DIR.exists():
        return None
    jobs = sorted(QUEUE_DIR.glob("*.json"), key=lambda p: p.stat().st_mtime)
    if not jobs:
        return None
    path = jobs[0]
    try:
        with open(path, "r", encoding="utf-8") as f:
            job = json.load(f)
        path.unlink()
        return job
    except Exception:
        return None
