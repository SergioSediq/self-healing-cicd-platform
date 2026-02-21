"""Alerting integration (Slack, PagerDuty)."""
import os
import json

SLACK_WEBHOOK = os.getenv("SLACK_WEBHOOK_URL")
PAGERDUTY_KEY = os.getenv("PAGERDUTY_ROUTING_KEY")


def send_slack(message: str, level: str = "error") -> bool:
    if not SLACK_WEBHOOK:
        return False
    try:
        import urllib.request
        payload = json.dumps({
            "text": message,
            "attachments": [{"color": "danger" if level == "error" else "warning", "text": message}],
        }).encode()
        req = urllib.request.Request(SLACK_WEBHOOK, data=payload, method="POST")
        req.add_header("Content-Type", "application/json")
        urllib.request.urlopen(req, timeout=5)
        return True
    except Exception:
        return False


def send_pagerduty(summary: str, severity: str = "error") -> bool:
    if not PAGERDUTY_KEY:
        return False
    try:
        import urllib.request
        payload = json.dumps({
            "routing_key": PAGERDUTY_KEY,
            "event_action": "trigger",
            "payload": {"summary": summary, "severity": severity},
        }).encode()
        req = urllib.request.Request("https://events.pagerduty.com/v2/enqueue", data=payload, method="POST")
        req.add_header("Content-Type", "application/json")
        urllib.request.urlopen(req, timeout=5)
        return True
    except Exception:
        return False


def alert_heal_failures(run_id: str, error_msg: str, consecutive_count: int) -> None:
    if consecutive_count >= int(os.getenv("ALERT_FAILURE_THRESHOLD", "3")):
        msg = f"Heal agent failed {consecutive_count} times. Run: {run_id}. Error: {error_msg}"
        send_slack(msg)
        send_pagerduty(msg)
