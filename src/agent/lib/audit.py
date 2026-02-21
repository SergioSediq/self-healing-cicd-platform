"""Audit logging for agent edits and commits."""
import json
import os
import time
from pathlib import Path

AUDIT_LOG = Path("logs/agent_audit.jsonl")
AUDIT_LOG.parent.mkdir(parents=True, exist_ok=True)


def log_audit(
    event: str,
    run_id: str,
    provider: str,
    details: dict | None = None,
) -> None:
    """Append an audit event to the audit log."""
    if os.getenv("AUDIT_DISABLED", "").lower() in ("1", "true", "yes"):
        return
    try:
        entry = {
            "ts": time.time(),
            "event": event,
            "run_id": run_id,
            "provider": provider,
            "details": details or {},
        }
        with open(AUDIT_LOG, "a", encoding="utf-8") as f:
            f.write(json.dumps(entry, default=str) + "\n")
    except Exception as e:
        print(f"⚠️ Audit log write failed: {e}")
