"""Output validation and guardrails."""
import re
from pathlib import Path

DANGEROUS_PATH_PATTERNS = [
    r"/etc/passwd", r"/etc/shadow", r"\.\./\.\./",
    r"^/\s*bin/", r"^/\s*usr/bin/", r"\.env$", r"\.aws/credentials",
]
RESTRICTED_FILES = {"package-lock.json", "yarn.lock", ".env", ".gitignore"}
RESTRICTED_EXTENSIONS = {".pem", ".key", ".crt", ".p12"}


def is_path_allowed(file_path: str, allow_restricted: bool = False) -> tuple[bool, str]:
    """
    Check if file path is allowed for modification.
    Returns (allowed, reason).
    """
    path = Path(file_path)
    normalized = str(path.resolve())

    for pattern in DANGEROUS_PATH_PATTERNS:
        if re.search(pattern, normalized):
            return False, f"Blocked: dangerous path pattern {pattern}"

    if path.name in RESTRICTED_FILES and not allow_restricted:
        return False, f"Blocked: restricted file {path.name}"

    if path.suffix.lower() in RESTRICTED_EXTENSIONS:
        return False, f"Blocked: sensitive extension {path.suffix}"

    # Block path traversal
    if ".." in file_path:
        return False, "Blocked: path traversal"

    return True, ""


def validate_llm_output_corrected_code(code: str) -> tuple[bool, str]:
    """Check for potential injection in generated code."""
    suspicious = [
        (r"import\s+os\s*;\s*os\.system", "shell execution"),
        (r"subprocess\.(run|call|Popen)\s*\(", "subprocess call"),
        (r"eval\s*\(", "eval"),
        (r"__import__\s*\(", "dynamic import"),
        (r"exec\s*\(", "exec"),
    ]
    for pat, desc in suspicious:
        if re.search(pat, code):
            return False, f"Suspicious: {desc}"
    return True, ""
