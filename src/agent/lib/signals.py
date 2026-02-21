"""Graceful shutdown handling."""
import signal
import sys

_shutdown_requested = False


def _handler(signum, frame):
    global _shutdown_requested
    _shutdown_requested = True
    # Allow second SIGTERM to force exit
    signal.signal(signal.SIGTERM, signal.SIG_DFL)
    signal.signal(signal.SIGINT, signal.SIG_DFL)


def setup_graceful_shutdown():
    signal.signal(signal.SIGTERM, _handler)
    signal.signal(signal.SIGINT, _handler)


def is_shutdown_requested() -> bool:
    return _shutdown_requested


def check_shutdown():
    if _shutdown_requested:
        sys.exit(130)
