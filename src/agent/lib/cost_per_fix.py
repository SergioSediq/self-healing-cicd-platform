"""Cost per fix: aggregate token cost by successful fix."""
import json
from pathlib import Path

TOKEN_LOG = Path(os.getenv("TOKEN_LOG_PATH", "logs/token_usage.jsonl"))
AUDIT_LOG = Path(os.getenv("AUDIT_LOG_PATH", "logs/agent_audit.jsonl"))
# Approximate $/1K tokens (Gemini)
INPUT_COST_PER_1K = float(__import__("os").getenv("COST_INPUT_PER_1K", "0.0001"))
OUTPUT_COST_PER_1K = float(__import__("os").getenv("COST_OUTPUT_PER_1K", "0.0003"))


def get_cost_per_fix(correlation_ids: set[str] | None = None) -> dict:
    """Return total cost and cost per fix for given correlation_ids (or all fixes)."""
    fix_ids = set()
    if AUDIT_LOG.exists():
        for line in open(AUDIT_LOG, encoding="utf-8"):
            try:
                e = json.loads(line.strip())
                if e.get("event") == "fix_applied":
                    fix_ids.add(e.get("details", {}).get("correlation_id") or e.get("ts"))
            except Exception:
                pass
    if correlation_ids:
        fix_ids &= correlation_ids
    total_input = total_output = 0
    if TOKEN_LOG.exists():
        for line in open(TOKEN_LOG, encoding="utf-8"):
            try:
                e = json.loads(line.strip())
                cid = e.get("correlation_id")
                if not fix_ids or cid in fix_ids:
                    total_input += e.get("input_tokens", 0)
                    total_output += e.get("output_tokens", 0)
            except Exception:
                pass
    cost = (total_input / 1000 * INPUT_COST_PER_1K) + (total_output / 1000 * OUTPUT_COST_PER_1K)
    return {
        "total_cost_usd": round(cost, 6),
        "fixes_count": len(fix_ids),
        "cost_per_fix_usd": round(cost / len(fix_ids), 6) if fix_ids else 0,
    }
