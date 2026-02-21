"""Token usage tracking for cost/budget alerts."""
import os
import json
from pathlib import Path
from threading import Lock

TOKEN_LOG = Path(os.getenv("TOKEN_LOG_PATH", "logs/token_usage.jsonl"))
BUDGET_ALERT_THRESHOLD = int(os.getenv("TOKEN_BUDGET_ALERT", "100000"))  # tokens per run/session
_lock = Lock()


def log_token_usage(run_id: str, model: str, input_tokens: int, output_tokens: int, correlation_id: str | None = None) -> None:
    """Log token usage for analytics."""
    TOKEN_LOG.parent.mkdir(parents=True, exist_ok=True)
    entry = {
        "run_id": run_id,
        "model": model,
        "input_tokens": input_tokens,
        "output_tokens": output_tokens,
        "total": input_tokens + output_tokens,
        "correlation_id": correlation_id,
    }
    with _lock:
        with open(TOKEN_LOG, "a", encoding="utf-8") as f:
            f.write(json.dumps(entry) + "\n")


def get_session_tokens(correlation_id: str | None = None) -> int:
    """Sum tokens for current session (by correlation_id or recent entries)."""
    if not TOKEN_LOG.exists():
        return 0
    total = 0
    with open(TOKEN_LOG, "r", encoding="utf-8") as f:
        for line in f:
            try:
                e = json.loads(line.strip())
                if correlation_id and e.get("correlation_id") != correlation_id:
                    continue
                total += e.get("total", 0)
            except Exception:
                pass
    return total


def check_budget_alert(correlation_id: str | None) -> bool:
    """Return True if over budget (caller may trigger alert)."""
    return get_session_tokens(correlation_id) >= BUDGET_ALERT_THRESHOLD
