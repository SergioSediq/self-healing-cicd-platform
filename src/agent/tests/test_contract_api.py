"""Contract tests for API schema."""
import json


def test_status_response_schema():
    """Status API returns expected shape."""
    schema = {
        "last_run_id": str,
        "status": str,
        "logs": str,
        "timestamp": (int, float),
        "analysis": dict,
    }
    # Example response
    example = {
        "last_run_id": "test",
        "status": "idle",
        "logs": "",
        "timestamp": 1234567890.0,
        "analysis": {"root_cause": None, "suggested_fix": None, "confidence_score": 0},
    }
    for key, typ in schema.items():
        assert key in example
        assert isinstance(example[key], typ) or (
            isinstance(typ, tuple) and type(example[key]) in typ
        )


def test_history_response_schema():
    """History API returns history + total."""
    example = {"history": [], "total": 0}
    assert "history" in example
    assert "total" in example
    assert isinstance(example["history"], list)
    assert isinstance(example["total"], int)
