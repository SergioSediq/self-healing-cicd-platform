"""Feature flags via environment variables."""
import os


def is_enabled(flag: str) -> bool:
    key = f"FEATURE_{flag.upper()}"
    return os.getenv(key, "").lower() in ("1", "true", "yes")


# Common flags
QUORUM = lambda: is_enabled("quorum")
STREAMING = lambda: is_enabled("streaming")
PRE_VERIFY = lambda: not os.getenv("SKIP_PRE_VERIFY", "").lower() in ("1", "true", "yes")
RECOVERY_MODE = lambda: is_enabled("recovery")
JIRA_ON_LOW_CONFIDENCE = lambda: is_enabled("jira_on_low_confidence")
