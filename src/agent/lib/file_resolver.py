"""Smart file resolution with caching and monorepo handling."""
from pathlib import Path
from functools import lru_cache

# Simple in-memory cache for file lookups (resets per process)
_file_cache: dict[str, Path | None] = {}


def find_file(filename: str, project_root: Path | None = None) -> Path | None:
    """
    Recursively searches for a file with smarter prioritization.
    Prefers: src/, then root, excludes node_modules, __pycache__, .git.
    """
    root = project_root or Path(".")
    key = f"{root}:{filename}"
    if key in _file_cache:
        return _file_cache[key]

    base = filename.split("/")[-1] if "/" in filename else filename
    matches: list[Path] = []
    for p in root.rglob(base):
        if any(x in p.parts for x in ("node_modules", "__pycache__", ".git", "venv", ".venv")):
            continue
        if p.is_file() and p.name == base:
            matches.append(p)

    if not matches:
        _file_cache[key] = None
        return None

    # Prefer exact path match first
    for m in matches:
        if str(m).replace("\\", "/").endswith(filename.replace("\\", "/")):
            _file_cache[key] = m
            return m

    # Then prefer src/
    src_matches = [m for m in matches if "src" in str(m)]
    if src_matches:
        best = min(src_matches, key=lambda p: len(p.parts))
        _file_cache[key] = best
        return best

    best = min(matches, key=lambda p: len(p.parts))
    _file_cache[key] = best
    return best


def clear_cache() -> None:
    """Clear the file resolution cache (e.g. for tests)."""
    _file_cache.clear()
