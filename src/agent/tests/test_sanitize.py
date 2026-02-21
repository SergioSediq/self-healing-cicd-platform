"""Tests for sanitize module."""
from lib.sanitize import mask_secrets, sanitize_logs


def test_mask_secrets():
    assert "***REDACTED***" in mask_secrets("password=secret123")
    assert "***REDACTED***" in mask_secrets("Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9")


def test_sanitize_logs_empty():
    assert sanitize_logs("") == ""

