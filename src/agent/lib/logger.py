"""Structured JSON logging with correlation IDs."""
import json
import os
import sys
from contextvars import ContextVar

correlation_id_var: ContextVar[str | None] = ContextVar("correlation_id", default=None)
USE_JSON = os.getenv("LOG_JSON", "1").lower() in ("1", "true", "yes")


def _log(level: str, msg: str, **extra) -> None:
    if USE_JSON:
        obj = {"level": level, "message": msg}
        cid = correlation_id_var.get()
        if cid:
            obj["correlation_id"] = cid
        obj.update(extra)
        print(json.dumps(obj), file=sys.stderr)
    else:
        cid = correlation_id_var.get()
        prefix = f"[{level}]"
        if cid:
            prefix += f" [{cid}]"
        print(f"{prefix} {msg}", file=sys.stderr)
        for k, v in extra.items():
            print(f"  {k}={v}", file=sys.stderr)


def info(msg: str, **extra) -> None:
    _log("INFO", msg, **extra)


def warn(msg: str, **extra) -> None:
    _log("WARN", msg, **extra)


def error(msg: str, **extra) -> None:
    _log("ERROR", msg, **extra)


def debug(msg: str, **extra) -> None:
    if os.getenv("DEBUG"):
        _log("DEBUG", msg, **extra)
