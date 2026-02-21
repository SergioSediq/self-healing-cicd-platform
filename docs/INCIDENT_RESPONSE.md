# Incident Response & Recovery Playbook

## Overview

This document covers incident response for the Self-Healing CI/CD platform.

## Severity Levels

- **P1 Critical**: Pipeline completely broken, agent unable to heal
- **P2 High**: Agent produces incorrect fixes, security issues
- **P3 Medium**: Dashboard unreachable, non-blocking errors

## Recovery Procedures

### Agent Produces Wrong Fixes

1. Disable auto-heal: set `CONFIDENCE_THRESHOLD=1.0` to prevent auto-apply
2. Review `logs/agent_audit.jsonl` for recent fix events
3. Revert the offending commit: `git revert <commit>`
4. Investigate root cause (log quality, model, prompt)
5. Re-enable when fixed

### LLM API Failures (Rate Limit, Timeout)

1. Agent uses fallback model automatically
2. Check `LLM_MAX_RETRIES` and `LLM_REQUEST_TIMEOUT`
3. Consider increasing `RATE_LIMIT_DELAY`
4. Verify API quota in Google Cloud Console

### CI Pipeline Stuck

1. Cancel the workflow in GitHub Actions
2. Check if auto-heal job ran and created a branch
3. If fix branch exists, review and merge manually
4. If no fix: run agent locally with `--logs "$(cat build_logs.txt)"` and `--provider github`

### Dashboard Auth Bypass

1. Set `DASHBOARD_API_KEY` in production
2. Ensure API routes use `requireAuth`
3. Rotate key if compromised

## Rollback

```bash
# Revert last agent commit
git revert HEAD --no-edit
git push origin main
```

## Contacts

- On-call: [Define in your org]
- Escalation: [Define in your org]
