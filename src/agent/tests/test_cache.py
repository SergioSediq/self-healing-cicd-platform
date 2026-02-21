"""Tests for cache module."""
import os

import pytest
from lib.cache import get_cached_analysis, set_cached_analysis


@pytest.fixture(autouse=True)
def disable_cache(monkeypatch):
    monkeypatch.delenv("CACHE_DISABLED", raising=False)


def test_cache_miss():
    assert get_cached_analysis("unique log content abc 123") is None


def test_cache_roundtrip():
    content = "test log for cache roundtrip"
    data = {"root_cause": "test", "confidence_score": 0.8}
    set_cached_analysis(content, data)
    result = get_cached_analysis(content)
    assert result is not None
    assert result["root_cause"] == "test"
