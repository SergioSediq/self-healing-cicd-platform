# Deployment Guide

## Docker Compose

```bash
docker-compose up -d
# Dashboard: http://localhost:3000
# With monitoring: docker-compose --profile monitoring up -d
```

## Helm

```bash
helm install heal ./helm/heal-platform -n autopilot-target --create-namespace
```

## Argo CD / Flux (GitOps)

1. Create an Application manifest pointing to this repo's `helm/heal-platform` or `infra/k8s/`.
2. Sync on push to main.

Example Argo CD Application:
```yaml
apiVersion: argoproj.io/v1alpha1
kind: Application
metadata:
  name: heal-platform
spec:
  source:
    repoURL: https://github.com/your-org/self-healing-cicd-ai-ops-integration
    path: helm/heal-platform
    targetRevision: main
  destination:
    server: https://kubernetes.default.svc
    namespace: autopilot-target
```

## Multi-Region

Deploy separate instances per region. Use `AUDIT_LOG_DIR` and provider env vars per region. Consider shared storage (S3, EFS) for audit logs if needed for centralized analytics.

## Backup & Restore

- **Audit logs**: `logs/agent_audit.jsonl` — back up regularly. Restore by copying file back.
- **Token usage**: `logs/token_usage.jsonl` — optional for cost analysis.
- **Status**: `src/dashboard/public/status.json` — ephemeral, no backup needed.
