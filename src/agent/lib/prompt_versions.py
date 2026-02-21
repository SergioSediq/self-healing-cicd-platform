"""Prompt versioning for A/B testing."""
import os
from pathlib import Path

PROMPTS_DIR = Path(os.getenv("PROMPTS_DIR", "prompts"))


def get_prompt(version: str, name: str) -> str:
    path = PROMPTS_DIR / version / f"{name}.txt"
    if path.exists():
        return path.read_text(encoding="utf-8")
    return ""


def list_versions() -> list[str]:
    if not PROMPTS_DIR.exists():
        return ["default"]
    return [d.name for d in PROMPTS_DIR.iterdir() if d.is_dir()]
