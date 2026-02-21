"""Simulate failures for local development."""
import random

FAILURE_TYPES = [
    ("FIX_APPLIED", " missing. Test suite failed."),
    ("npm ERR! 404", " Not Found: package 'typo-pkg@1.0.0'"),
    ("SyntaxError", " Unexpected token in test.js:42"),
]


def get_simulated_logs(failure_type: str | None = None) -> str:
    if not failure_type:
        failure_type = random.choice([f[0] for f in FAILURE_TYPES])
    for k, suffix in FAILURE_TYPES:
        if k in failure_type:
            return f"""
> node test.js
❌ CRITICAL ERROR: {k}{suffix}
npm ERR! Test failed.
"""
    return FAILURE_TYPES[0][1]
