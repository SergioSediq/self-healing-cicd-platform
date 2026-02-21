"""Central configuration schema and validation."""
import os
from functools import lru_cache
from typing import Optional

from pydantic import BaseModel, Field, field_validator


class AgentConfig(BaseModel):
    """Agent configuration with validation."""

    google_api_key: str = Field(..., description="Google Gemini API key")
    project_root: str = Field(default="src", description="Project root path")
    dashboard_status_file: str = Field(
        default="src/dashboard/public/status.json",
        description="Path to dashboard status JSON",
    )
    log_max_chars: int = Field(default=16000, ge=1000, le=100000, description="Max log chars for LLM")
    confidence_threshold: float = Field(default=0.8, ge=0.0, le=1.0)
    primary_model: str = Field(default="gemini-2.0-flash", description="Primary LLM model")
    fallback_model: str = Field(default="gemini-1.5-flash", description="Fallback LLM model")
    max_retries: int = Field(default=3, ge=1, le=10)
    request_timeout: int = Field(default=120, ge=30)
    rate_limit_delay_seconds: float = Field(default=1.0, ge=0.1)

    @field_validator("google_api_key")
    @classmethod
    def validate_api_key(cls, v: str) -> str:
        if not v or not v.strip():
            raise ValueError("GOOGLE_API_KEY cannot be empty")
        return v.strip()


def _load_env(key: str, default: Optional[str] = None) -> str:
    val = os.getenv(key, default or "")
    return val.strip() if isinstance(val, str) else ""


@lru_cache(maxsize=1)
def load_config() -> AgentConfig:
    """Load and validate configuration from environment."""
    key = _load_env("GOOGLE_API_KEY")
    if not key:
        raise ValueError("GOOGLE_API_KEY is required. Set it in .env or environment.")
    return AgentConfig(
        google_api_key=key,
        project_root=_load_env("PROJECT_ROOT") or "src",
        dashboard_status_file=_load_env("DASHBOARD_STATUS_FILE") or "src/dashboard/public/status.json",
        log_max_chars=int(_load_env("LOG_MAX_CHARS") or "16000"),
        confidence_threshold=float(_load_env("CONFIDENCE_THRESHOLD") or "0.8"),
        primary_model=_load_env("LLM_PRIMARY_MODEL") or "gemini-2.0-flash",
        fallback_model=_load_env("LLM_FALLBACK_MODEL") or "gemini-1.5-flash",
        max_retries=int(_load_env("LLM_MAX_RETRIES") or "3"),
        request_timeout=int(_load_env("LLM_REQUEST_TIMEOUT") or "120"),
        rate_limit_delay_seconds=float(_load_env("RATE_LIMIT_DELAY") or "1.0"),
    )
