"""Tests for CI providers."""
import os
import pytest
from lib.providers import (
    LocalProvider,
    GitHubActionsProvider,
    JenkinsProvider,
    get_provider,
)


def test_local_provider():
    p = LocalProvider()
    logs = p.fetch_logs("test")
    assert "FIX_APPLIED" in logs
    assert "Local" in p.get_context()
    ok, _ = p.validate_env()
    assert ok is True


def test_github_provider_no_token(monkeypatch):
    monkeypatch.delenv("GITHUB_TOKEN", raising=False)
    p = GitHubActionsProvider()
    logs = p.fetch_logs("123")
    assert "GITHUB_TOKEN" in logs or "Error" in logs


def test_jenkins_provider_validate_env(monkeypatch):
    monkeypatch.delenv("JENKINS_URL", raising=False)
    p = JenkinsProvider()
    ok, msg = p.validate_env()
    assert ok is False
    assert "JENKINS_URL" in msg


def test_get_provider():
    assert isinstance(get_provider("local"), LocalProvider)
    assert isinstance(get_provider("github"), GitHubActionsProvider)
    assert isinstance(get_provider("LOCAL"), LocalProvider)
