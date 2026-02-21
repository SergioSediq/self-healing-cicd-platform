"""Webhook: notify external systems on heal events."""
import json
import os
import urllib.request


def fire_webhook(event: str, payload: dict) -> bool:
    url = os.getenv("WEBHOOK_URL")
    if not url:
        return False
    try:
        data = json.dumps({"event": event, "payload": payload}).encode()
        req = urllib.request.Request(url, data=data, method="POST")
        req.add_header("Content-Type", "application/json")
        if os.getenv("WEBHOOK_SECRET"):
            req.add_header("X-Webhook-Secret", os.getenv("WEBHOOK_SECRET"))
        urllib.request.urlopen(req, timeout=5)
        return True
    except Exception:
        return False
