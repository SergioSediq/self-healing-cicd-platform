"""Input sanitization and secret masking."""
import re
from typing import List

# Common secret patterns
SECRET_PATTERNS = [
    (re.compile(r'(password|passwd|pwd|secret|token|api[_-]?key|auth)\s*[:=]\s*["\']?([^\s"\']+)', re.I), r'\1=***REDACTED***'),
    (re.compile(r'Bearer\s+[A-Za-z0-9\-_\.]+'), 'Bearer ***REDACTED***'),
    (re.compile(r'(-----BEGIN [A-Z ]+-----)[\s\S]+?(-----END [A-Z ]+-----)'), r'\1***REDACTED***\2'),
    (re.compile(r'[A-Za-z0-9+/]{50,}={0,2}'), '***REDACTED***'),  # long base64-like strings
]
MAX_INPUT_BYTES = 10 * 1024 * 1024  # 10MB


def mask_secrets(text: str) -> str:
    """Redact common secret patterns from text."""
    out = text
    for pattern, repl in SECRET_PATTERNS:
        out = pattern.sub(repl, out)
    return out


def sanitize_logs(logs: str, max_bytes: int = MAX_INPUT_BYTES) -> str:
    """Validate and sanitize log input before LLM."""
    if not isinstance(logs, str):
        return ""
    # Truncate by bytes
    encoded = logs.encode("utf-8", errors="replace")
    if len(encoded) > max_bytes:
        logs = encoded[:max_bytes].decode("utf-8", errors="replace") + "\n...[truncated]"
    return mask_secrets(logs)


# Dangerous file patterns that guardrails should block
DANGEROUS_PATH_PATTERNS = [
    r"/etc/passwd",
    r"/etc/shadow",
    r"\.\./\.\./",  # path traversal
    r"^/\s*bin/",
    r"^/\s*usr/bin/",
    r"\.env$",
    r"\.aws/credentials",
]
