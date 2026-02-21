"""Tests for llm_utils."""
import pytest
from lib.llm_utils import truncate_logs_smart, extract_error_region, with_retry


def test_truncate_logs_short():
    logs = "short log"
    assert truncate_logs_smart(logs, max_chars=100) == logs


def test_truncate_logs_long():
    logs = "x" * 20000
    out = truncate_logs_smart(logs, max_chars=1000)
    assert len(out) <= 1200
    assert "[TRUNCATED" in out


def test_extract_error_region():
    logs = "a" * 500 + "error: something went wrong" + "b" * 500
    region = extract_error_region(logs, window=100)
    assert "error:" in region.lower()


def test_with_retry_success():
    count = [0]
    def fn():
        count[0] += 1
        return 42
    assert with_retry(fn, max_retries=3) == 42
    assert count[0] == 1


def test_with_retry_eventually_succeeds():
    count = [0]
    def fn():
        count[0] += 1
        if count[0] < 2:
            raise ValueError("fail")
        return 42
    assert with_retry(fn, max_retries=3, delay=0.01) == 42
    assert count[0] == 2


def test_with_retry_fails():
    def fn():
        raise ValueError("always fail")
    with pytest.raises(ValueError):
        with_retry(fn, max_retries=2, delay=0.01)
