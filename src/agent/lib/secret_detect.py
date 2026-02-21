"""Secret detection in LLM output - block before applying."""
import re

PATTERNS = [
    re.compile(r'[A-Za-z0-9+/]{40,}={0,2}'),  # long base64
    re.compile(r'(?i)(password|secret|api[_-]?key|token)\s*[:=]\s*["\']?[^\s"\']{8,}'),
    re.compile(r'(?i)Bearer\s+[A-Za-z0-9\-_.]{20,}'),
    re.compile(r'-----BEGIN [A-Z ]+-----[\s\S]+?-----END [A-Z ]+-----'),
]


def has_secret(content: str) -> tuple[bool, str]:
    """Return (has_secret, matched_pattern_desc)."""
    for p in PATTERNS:
        if p.search(content):
            return True, f"Possible secret pattern: {p.pattern[:50]}..."
    return False, ""
