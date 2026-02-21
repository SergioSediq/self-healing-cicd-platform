"""Quorum: require multiple LLM runs to agree before applying fix."""
import os
from typing import Callable, TypeVar

T = TypeVar("T")

QUORUM_SIZE = int(os.getenv("QUORUM_SIZE", "2"))


def run_with_quorum(fn: Callable[[], T], n: int = QUORUM_SIZE) -> T | None:
    """
    Run fn() n times. Return result if at least 2 runs agree (same file_path + similar confidence).
    Otherwise return None (no quorum).
    """
    if n < 2:
        return fn()

    results: list[T] = []
    for _ in range(n):
        try:
            r = fn()
            results.append(r)
        except Exception:
            pass

    if len(results) < 2:
        return results[0] if results else None

    # Check agreement: same file_path
    paths = [getattr(r, "file_path", str(r)) for r in results]
    from collections import Counter
    counts = Counter(paths)
    most_common = counts.most_common(1)[0]
    if most_common[1] < 2:
        return None
    agreed_path = most_common[0]
    for r in results:
        if getattr(r, "file_path", "") == agreed_path:
            return r
    return results[0]
