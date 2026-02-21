"""Rollback: undo last fix or multiple fixes (undo stack)."""
import json
import os
from pathlib import Path

AUDIT_LOG = Path(os.getenv("AUDIT_LOG_PATH", "logs/agent_audit.jsonl"))
BACKUP_DIR = Path(os.getenv("BACKUP_DIR", "logs/backups"))


def get_fix_history(limit: int = 10) -> list[dict]:
    """Return list of fix_applied events (newest first)."""
    if not AUDIT_LOG.exists():
        return []
    fixes = []
    with open(AUDIT_LOG, "r", encoding="utf-8") as f:
        for line in f:
            try:
                e = json.loads(line.strip())
                if e.get("event") == "fix_applied":
                    fixes.append(e)
            except Exception:
                pass
    return list(reversed(fixes[-limit:]))


def get_last_fix() -> dict | None:
    """Get last fix_applied event from audit log."""
    if not AUDIT_LOG.exists():
        return None
    last = None
    with open(AUDIT_LOG, "r", encoding="utf-8") as f:
        for line in f:
            try:
                e = json.loads(line.strip())
                if e.get("event") == "fix_applied":
                    last = e
            except Exception:
                pass
    return last


def rollback_last() -> tuple[bool, str]:
    """
    Rollback the last fix by restoring from backup.
    Backups are created at logs/backups/<filepath_hash>_<ts>.bak when applying fix.
    Returns (success, message).
    """
    last = get_last_fix()
    if not last:
        return False, "No fix to rollback"
    details = last.get("details", {})
    file_path = details.get("file")
    if not file_path:
        return False, "No file path in last fix"
    backup_dir = BACKUP_DIR
    if not backup_dir.exists():
        return False, "No backup directory"
    # Find most recent backup for this file
    stem = Path(file_path).name
    backups = sorted(backup_dir.glob(f"*{stem}*.bak"), key=lambda p: p.stat().st_mtime, reverse=True)
    if not backups:
        return False, f"No backup found for {file_path}"
    try:
        with open(backups[0], "r", encoding="utf-8") as f:
            content = f.read()
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(content)
        return True, f"Restored {file_path} from backup"
    except Exception as e:
        return False, str(e)


def _restore_from_backup(file_path: str, backup_path: str | None) -> bool:
    if backup_path and Path(backup_path).exists():
        try:
            with open(backup_path, "r", encoding="utf-8") as bf:
                content = bf.read()
            Path(file_path).parent.mkdir(parents=True, exist_ok=True)
            with open(file_path, "w", encoding="utf-8") as tf:
                tf.write(content)
            return True
        except Exception:
            pass
    stem = Path(file_path).name
    if BACKUP_DIR.exists():
        backups = sorted(
            BACKUP_DIR.glob(f"*{stem}*.bak"),
            key=lambda p: p.stat().st_mtime,
            reverse=True,
        )
        if backups:
            try:
                with open(backups[0], "r", encoding="utf-8") as bf:
                    content = bf.read()
                with open(file_path, "w", encoding="utf-8") as tf:
                    tf.write(content)
                return True
            except Exception:
                pass
    return False


def rollback_n(n: int = 1) -> tuple[bool, str]:
    """Undo last n fixes. n=1 is equivalent to rollback_last()."""
    fixes = get_fix_history(limit=100)
    to_undo = fixes[-n:] if len(fixes) >= n else fixes
    success_count = 0
    for f in reversed(to_undo):
        details = f.get("details", {})
        file_path = details.get("file")
        backup_path = details.get("backup")
        if file_path and _restore_from_backup(file_path, backup_path):
            success_count += 1
    return success_count == len(to_undo), f"Rolled back {success_count}/{len(to_undo)} fix(es)"
