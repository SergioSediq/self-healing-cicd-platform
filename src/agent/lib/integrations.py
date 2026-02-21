"""Integrations: Slack, Teams, Discord, Jira, ServiceNow, PagerDuty."""
import os
import json
import urllib.request


def _b64(s: str) -> str:
    import base64
    return base64.b64encode(s.encode()).decode().strip()


def slack_notify(message: str, webhook: str | None = None) -> bool:
    w = webhook or os.getenv("SLACK_WEBHOOK_URL")
    if not w:
        return False
    try:
        data = json.dumps({"text": message}).encode()
        req = urllib.request.Request(w, data=data, method="POST")
        req.add_header("Content-Type", "application/json")
        urllib.request.urlopen(req, timeout=5)
        return True
    except Exception:
        return False


def teams_notify(message: str, webhook: str | None = None) -> bool:
    w = webhook or os.getenv("TEAMS_WEBHOOK_URL")
    if not w:
        return False
    try:
        payload = {"@type": "MessageCard", "text": message}
        req = urllib.request.Request(w, data=json.dumps(payload).encode(), method="POST")
        req.add_header("Content-Type", "application/json")
        urllib.request.urlopen(req, timeout=5)
        return True
    except Exception:
        return False


def discord_notify(message: str, webhook: str | None = None) -> bool:
    w = webhook or os.getenv("DISCORD_WEBHOOK_URL")
    if not w:
        return False
    try:
        req = urllib.request.Request(w, data=json.dumps({"content": message[:2000]}).encode(), method="POST")
        req.add_header("Content-Type", "application/json")
        urllib.request.urlopen(req, timeout=5)
        return True
    except Exception:
        return False


def jira_create_issue(summary: str, description: str, project: str | None = None) -> str | None:
    url = os.getenv("JIRA_URL", "").rstrip("/")
    token = os.getenv("JIRA_API_TOKEN")
    email = os.getenv("JIRA_EMAIL")
    proj = project or os.getenv("JIRA_PROJECT", "HEAL")
    if not url or not token or not email:
        return None
    try:
        payload = {
            "fields": {
                "project": {"key": proj},
                "summary": summary[:255],
                "description": {"type": "doc", "version": 1, "content": [{"type": "paragraph", "content": [{"type": "text", "text": description}]}]},
                "issuetype": {"name": "Task"},
            }
        }
        req = urllib.request.Request(f"{url}/rest/api/3/issue", data=json.dumps(payload).encode(), method="POST")
        req.add_header("Content-Type", "application/json")
        req.add_header("Authorization", f"Basic {_b64(f'{email}:{token}')}")
        with urllib.request.urlopen(req, timeout=10) as r:
            return json.loads(r.read().decode()).get("key")
    except Exception:
        return None


def servicenow_create_incident(short_desc: str, description: str) -> str | None:
    url = os.getenv("SERVICENOW_URL", "").rstrip("/")
    user = os.getenv("SERVICENOW_USER")
    pwd = os.getenv("SERVICENOW_PASSWORD")
    if not url or not user or not pwd:
        return None
    try:
        payload = {"short_description": short_desc[:160], "description": description}
        data = json.dumps(payload).encode()
        req = urllib.request.Request(f"{url}/api/now/table/incident", data=data, method="POST")
        req.add_header("Content-Type", "application/json")
        req.add_header("Authorization", f"Basic {_b64(f'{user}:{pwd}')}")
        with urllib.request.urlopen(req, timeout=10) as r:
            return json.loads(r.read().decode()).get("result", {}).get("number")
    except Exception:
        return None
