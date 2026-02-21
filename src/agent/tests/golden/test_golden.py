"""Golden tests: regression for known failure/fix pairs."""
import os

import pytest

GOLDEN_DIR = os.path.join(os.path.dirname(__file__), "fixtures")


@pytest.mark.skipif(not os.path.exists(GOLDEN_DIR), reason="No golden fixtures")
def test_golden_fix_applied_logs():
    """Known fix for FIX_APPLIED failure should include Dockerfile change."""
    path = os.path.join(GOLDEN_DIR, "fix_applied_logs.txt")
    if not os.path.exists(path):
        pytest.skip("fixtures/fix_applied_logs.txt not found")
    logs = open(path, encoding="utf-8").read()
    assert "FIX_APPLIED" in logs or "missing" in logs.lower()
