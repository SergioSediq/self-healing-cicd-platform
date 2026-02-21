"""Integration tests with mocked LLM."""
import os
from unittest.mock import patch

import pytest

pytest.importorskip("langchain")


@patch.dict(os.environ, {"GOOGLE_API_KEY": "test-key", "CACHE_DISABLED": "1"})
@patch("main.analyze_with_gemini")
def test_heal_flow_dry_run(mock_analyze):
    """Test full flow in dry-run mode with mocked LLM."""
    from main import run_heal, LogAnalysisResult
    import argparse

    mock_analyze.return_value = LogAnalysisResult(
        root_cause="Missing FIX_APPLIED",
        suggested_fix="Add ENV FIX_APPLIED=true",
        file_path="Dockerfile",
        confidence_score=0.95,
    )

    args = argparse.Namespace(
        run_id="test",
        provider="local",
        mode=None,
        logs=None,
        dry_run=True,
        rollback=False,
        rollback_n=1,
        simulate_failure=False,
    )
    code = run_heal(args)
    assert code == 0
    mock_analyze.assert_called_once()
