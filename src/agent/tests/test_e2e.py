"""End-to-end tests (optional, requires GOOGLE_API_KEY and network)."""
import os
import pytest

pytestmark = pytest.mark.skipif(
    not os.getenv("GOOGLE_API_KEY") or os.getenv("SKIP_E2E") == "1",
    reason="E2E tests require GOOGLE_API_KEY and are skipped by default",
)


def test_agent_local_e2e():
    """Run agent in local mode and verify it completes."""
    import subprocess
    result = subprocess.run(
        ["python", "main.py", "--provider", "local"],
        capture_output=True,
        text=True,
        cwd=os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
        timeout=60,
        env={**os.environ, "GOOGLE_API_KEY": os.environ["GOOGLE_API_KEY"]},
    )
    assert result.returncode == 0, f"Agent failed: {result.stderr}"
