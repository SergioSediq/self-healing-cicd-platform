"""SLO/SLA tracking: success rate, latency."""
import json
import os
from pathlib import Path

SLO_LOG = Path(os.getenv("SLO_LOG_PATH", "logs/slo.jsonl"))


def record_heal_run(success: bool, latency_ms: float, run_id: str = "") -> None:
    import time
    SLO_LOG.parent.mkdir(parents=True, exist_ok=True)
    with open(SLO_LOG, "a", encoding="utf-8") as f:
        f.write(json.dumps({"ts": time.time(), "success": success, "latency_ms": latency_ms, "run_id": run_id}) + "\n")


def get_slo_metrics(window_days: int = 7) -> dict:
    if not SLO_LOG.exists():
        return {"success_rate": 0, "avg_latency_ms": 0, "total": 0}
    cutoff = __import__("time").time() - window_days * 86400
    success = total = 0
    latencies = []
    with open(SLO_LOG, "r", encoding="utf-8") as f:
        for line in f:
            try:
                e = json.loads(line.strip())
                if e.get("ts", 0) >= cutoff:
                    total += 1
                    if e.get("success"):
                        success += 1
                    if "latency_ms" in e:
                        latencies.append(e["latency_ms"])
            except Exception:
                pass
    return {
        "success_rate": success / total if total else 0,
        "avg_latency_ms": sum(latencies) / len(latencies) if latencies else 0,
        "total": total,
    }
