"""LLM robustness: retries, fallback, rate limiting, log summarization."""
import re
import time
from typing import Callable, TypeVar

T = TypeVar("T")


def truncate_logs_smart(logs: str, max_chars: int = 16000) -> str:
    """
    Smarter log truncation: keep start (context) and end (failure).
    For large logs, preserve header + last N chars where errors typically appear.
    """
    if len(logs) <= max_chars:
        return logs

    header_chars = max_chars // 4
    tail_chars = max_chars - header_chars - 200
    header = logs[:header_chars]
    tail = logs[-tail_chars:]
    sep = "\n... [TRUNCATED - middle portion omitted] ...\n"
    return header + sep + tail


def extract_error_region(logs: str, window: int = 2000) -> str:
    """Extract region around common error markers to improve analysis."""
    markers = [
        r"error:|Error:|ERROR:|❌|failed|FATAL|Exception|Traceback",
        r"npm ERR!|Build failed|Test failed",
    ]
    for pattern in markers:
        match = re.search(pattern, logs, re.IGNORECASE)
        if match:
            start = max(0, match.start() - window // 2)
            end = min(len(logs), match.end() + window // 2)
            return logs[start:end]
    return logs[-window:] if len(logs) > window else logs


def with_retry(
    fn: Callable[[], T],
    max_retries: int = 3,
    delay: float = 1.0,
    backoff: float = 2.0,
) -> T:
    """Execute fn with exponential backoff retry."""
    last_error = None
    for attempt in range(max_retries):
        try:
            return fn()
        except Exception as e:
            last_error = e
            if attempt < max_retries - 1:
                sleep_time = delay * (backoff ** attempt)
                time.sleep(sleep_time)
    raise last_error  # type: ignore
