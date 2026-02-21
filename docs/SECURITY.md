# Security & Compliance

## Audit Retention
- Set `AUDIT_RETENTION_DAYS` (default 90). Run `python -m lib.retention` or cron.
- Archived logs go to `logs/archive/` as gzipped JSONL.

## Encryption at Rest
- For sensitive deployments, use encrypted volumes (LUKS, AWS EBS encryption).
- Store `logs/` on encrypted disk.

## SOC 2 Controls
- Access control: `DASHBOARD_VIEWER_KEY`, `DASHBOARD_APPROVER_KEY`
- Audit logging: `logs/agent_audit.jsonl`
- Change management: version control, code review

## Secret Rotation
- Rotate `GOOGLE_API_KEY`, `GITHUB_TOKEN` in provider secrets.
- Use `GOOGLE_API_KEY_ALT` with fallback: check both keys on failure.
- No downtime: update secret, then restart workers.
