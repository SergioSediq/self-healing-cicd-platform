"""Async CI providers using httpx."""
import asyncio
import base64
import os
from abc import ABC, abstractmethod

try:
    import httpx
    HAS_HTTPX = True
except ImportError:
    HAS_HTTPX = False

_http_client: "httpx.AsyncClient | None" = None


def get_client() -> "httpx.AsyncClient | None":
    global _http_client
    if HAS_HTTPX and _http_client is None:
        _http_client = httpx.AsyncClient(timeout=60.0)
    return _http_client


async def fetch_logs_async(provider_name: str, run_id: str) -> str:
    """Async fetch logs. Falls back to sync provider if httpx unavailable."""
    if not HAS_HTTPX:
        import lib.providers as prov
        loop = asyncio.get_event_loop()
        p = prov.get_provider(provider_name)
        return await loop.run_in_executor(None, p.fetch_logs, run_id)

    if provider_name == "github":
        repo = os.getenv("GITHUB_REPOSITORY", "user/repo")
        if os.path.exists("build_logs.txt"):
            with open("build_logs.txt", "r", encoding="utf-8", errors="replace") as f:
                return f.read()
        client = get_client()
        if not client:
            return "httpx not available"
        owner, repo_name = repo.split("/", 1)
        url = f"https://api.github.com/repos/{owner}/{repo_name}/actions/jobs/{run_id}/logs"
        headers = {
            "Authorization": f"Bearer {os.getenv('GITHUB_TOKEN', '')}",
            "Accept": "application/vnd.github+json",
        }
        r = await client.get(url, headers=headers)
        return r.text if r.status_code == 200 else f"Error: {r.status_code}"
    elif provider_name == "local":
        import lib.providers as prov
        p = prov.get_provider("local")
        return p.fetch_logs(run_id)
    else:
        import lib.providers as prov
        loop = asyncio.get_event_loop()
        p = prov.get_provider(provider_name)
        return await loop.run_in_executor(None, p.fetch_logs, run_id)
