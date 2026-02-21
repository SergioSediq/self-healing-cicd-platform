# Troubleshooting Decision Tree

```
Start: Heal failed or not working?
│
├─ Agent exits immediately
│  ├─ "GOOGLE_API_KEY not found" → Set GOOGLE_API_KEY in env
│  └─ "Provider config" error → Set provider env vars (see INTEGRATIONS.md)
│
├─ Analysis fails / LLM error
│  ├─ Rate limit → Wait, or increase RATE_LIMIT_DELAY
│  ├─ Circuit breaker open → Wait 60s or set CIRCUIT_BREAKER_TIMEOUT
│  └─ Invalid JSON from model → Enable FEATURE_RECOVERY_MODE
│
├─ Fix not applied
│  ├─ Confidence < threshold → Review manually, lower CONFIDENCE_THRESHOLD
│  ├─ Guardrail blocked → Check path (restricted files)
│  └─ Pre-verify failed → Fix syntax/lint in suggested code
│
├─ Dashboard shows "idle" / no data
│  ├─ Agent never ran locally → Run agent with --provider local
│  └─ status.json missing → Check DASHBOARD_STATUS_FILE path
│
└─ CI: Agent runs but no fix committed
   ├─ No file changes → Agent may have low confidence
   └─ Push failed → Check GITHUB_TOKEN permissions (contents: write)
```

## Quick Commands
- `python main.py --dry-run` — Test without applying
- `python main.py --rollback` — Undo last fix
- `python main.py --help` — See all options
