"""Error categorization for trending."""
import re

CATEGORIES = [
    (r"missing|not found|undefined|404", "missing_dependency"),
    (r"syntax|parse|invalid", "syntax_error"),
    (r"timeout|timed out", "timeout"),
    (r"permission|denied|403", "permission"),
    (r"rate limit|429", "rate_limit"),
    (r"connection refused|ECONNREFUSED", "connection"),
    (r"env|environment variable", "config"),
    (r"memory|OOM", "resource"),
]


def categorize_error(message: str) -> str:
    msg = (message or "").lower()
    for pattern, cat in CATEGORIES:
        if re.search(pattern, msg):
            return cat
    return "other"
