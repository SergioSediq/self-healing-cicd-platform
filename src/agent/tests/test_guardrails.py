"""Tests for guardrails."""
from lib.guardrails import is_path_allowed, validate_llm_output_corrected_code


def test_path_allowed():
    ok, _ = is_path_allowed("Dockerfile")
    assert ok is True


def test_path_blocked_restricted():
    ok, reason = is_path_allowed(".env")
    assert ok is False
    assert "blocked" in reason.lower()


def test_output_validation_clean():
    ok, _ = validate_llm_output_corrected_code("const x = 1;")
    assert ok is True


def test_output_validation_suspicious():
    ok, _ = validate_llm_output_corrected_code("import os; os.system('rm -rf /')")
    assert ok is False
