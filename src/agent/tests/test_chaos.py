"""Chaos testing: simulate LLM/provider failures."""
import pytest
from unittest.mock import patch, MagicMock


@patch.dict("os.environ", {"GOOGLE_API_KEY": "x", "CACHE_DISABLED": "1"})
@patch("main.analyze_with_gemini")
def test_chaos_llm_failure_recovery(mock_analyze):
    """When LLM fails, agent should exit with error."""
    mock_analyze.side_effect = RuntimeError("API rate limit")
    from main import run_heal
    import argparse
    args = argparse.Namespace(run_id="c", provider="local", mode=None, logs=None, dry_run=True, rollback=False, rollback_n=1, simulate_failure=False)
    code = run_heal(args)
    assert code == 1
