"""Model routing by log size/complexity."""
import os

PRIMARY = os.getenv("LLM_PRIMARY_MODEL", "gemini-2.0-flash")
FALLBACK = os.getenv("LLM_FALLBACK_MODEL", "gemini-1.5-flash")
LARGE_MODEL = os.getenv("LLM_LARGE_MODEL", PRIMARY)
SMALL_MODEL = os.getenv("LLM_SMALL_MODEL", "gemini-1.5-flash")
THRESHOLD_CHARS = int(os.getenv("MODEL_ROUTING_THRESHOLD", "8000"))


def route_model(logs: str) -> str:
    """Use large model for big logs, small for short."""
    if len(logs) > THRESHOLD_CHARS:
        return LARGE_MODEL
    return SMALL_MODEL
