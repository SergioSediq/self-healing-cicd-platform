"""Audit retention: auto-archive or delete old logs."""
import json
import os
import gzip
from pathlib import Path
from datetime import datetime, timedelta

AUDIT_LOG = Path(os.getenv("AUDIT_LOG_PATH", "logs/agent_audit.jsonl"))
ARCHIVE_DIR = Path(os.getenv("ARCHIVE_DIR", "logs/archive"))
RETENTION_DAYS = int(os.getenv("AUDIT_RETENTION_DAYS", "90"))


def run_retention() -> tuple[int, int]:
    """Archive entries older than RETENTION_DAYS. Returns (archived, deleted)."""
    if not AUDIT_LOG.exists():
        return 0, 0
    cutoff = (datetime.now() - timedelta(days=RETENTION_DAYS)).timestamp()
    kept = []
    archived = []
    with open(AUDIT_LOG, "r", encoding="utf-8") as f:
        for line in f:
            try:
                e = json.loads(line.strip())
                ts = e.get("ts", 0)
                if ts >= cutoff:
                    kept.append(line)
                else:
                    archived.append(e)
            except Exception:
                kept.append(line)
    if not archived:
        return 0, 0
    ARCHIVE_DIR.mkdir(parents=True, exist_ok=True)
    arch_path = ARCHIVE_DIR / f"audit_{int(cutoff)}.jsonl.gz"
    with gzip.open(arch_path, "wt", encoding="utf-8") as z:
        z.writelines(json.dumps(e) + "\n" for e in archived)
    with open(AUDIT_LOG, "w", encoding="utf-8") as f:
        f.writelines(kept)
    return len(archived), 0
