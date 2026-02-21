# GitHub Actions Runbook

## Setup
1. Add `GOOGLE_API_KEY` and `GITHUB_TOKEN` to repo secrets
2. Ensure workflow downloads `build_logs.txt` artifact before agent runs

## Common Issues
| Symptom | Cause | Fix |
|---------|-------|-----|
| Agent fails with `--mode` error | Old agent version | Ensure `main.py` has `--mode` arg |
| No logs for agent | Artifact not downloaded | Check `actions/download-artifact` step |
| 403 on push | Token permissions | Use `contents: write` in workflow |

## Rollback
```bash
git revert HEAD
git push
```
