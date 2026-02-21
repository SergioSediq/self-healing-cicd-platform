"""Property-based tests with Hypothesis."""
import pytest

hypothesis = pytest.importorskip("hypothesis")
from hypothesis import given, strategies as st


@given(st.text(min_size=1, max_size=1000))
def test_truncate_logs_smart_preserves_length_limit(s):
    from lib.llm_utils import truncate_logs_smart
    out = truncate_logs_smart(s, max_chars=100)
    assert len(out) <= 150


@given(st.text(alphabet="abc123\n", min_size=0, max_size=500))
def test_mask_secrets_no_crash(s):
    from lib.sanitize import mask_secrets
    mask_secrets(s)
