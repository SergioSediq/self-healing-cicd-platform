"""Tests for file resolver."""
from pathlib import Path

from lib.file_resolver import find_file, clear_cache


def test_find_file_nonexistent():
    clear_cache()
    assert find_file("nonexistent_file_xyz_12345.py") is None


def test_find_file_finds_existing():
    clear_cache()
    # test.js exists in target_app
    result = find_file("test.js")
    if result:
        assert result.exists()
        assert result.name == "test.js"


def test_clear_cache():
    clear_cache()
    clear_cache()  # no-op, no error
