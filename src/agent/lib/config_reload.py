"""Config hot reload: watch config file and reload on change."""
import os
import time
from pathlib import Path

CONFIG_FILE = Path(os.getenv("CONFIG_FILE", ".env"))


def watch_config(callback, interval: float = 5.0):
    """Poll config file mtime and call callback when changed."""
    mtime = _mtime()
    while True:
        time.sleep(interval)
        now = _mtime()
        if now and now != mtime:
            mtime = now
            try:
                callback()
            except Exception:
                pass


def _mtime() -> float | None:
    if CONFIG_FILE.exists():
        return CONFIG_FILE.stat().st_mtime
    return None
