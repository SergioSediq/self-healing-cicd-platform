# Setup & Troubleshooting Runbook

## Prerequisites

- Python 3.11+
- Node.js 18+
- Docker
- (Optional) Terraform, Kind, kubectl for K8s

## Quick Start

```bash
cp .env.example .env
# Edit .env with GOOGLE_API_KEY and GITHUB_TOKEN

# Run agent locally (mock logs)
cd src/agent && pip install -r requirements.txt
python main.py --provider local

# Run dashboard
cd src/dashboard && npm install && npm run dev
```

## Environment Variables

| Variable | Required | Description |
|----------|----------|-------------|
| GOOGLE_API_KEY | Yes | Google Gemini API key |
| GITHUB_TOKEN | Yes (CI) | GitHub personal access token |
| JENKINS_URL | Jenkins | Jenkins base URL |
| JENKINS_USER | Jenkins | Jenkins username |
| JENKINS_TOKEN | Jenkins | Jenkins API token |
| AWS_REGION | AWS | AWS region (default: us-east-1) |
| AZURE_DEVOPS_ORG | Azure | Azure DevOps org |
| AZURE_DEVOPS_PROJECT | Azure | Azure DevOps project |
| AZURE_DEVOPS_PAT | Azure | Azure DevOps PAT |

## Troubleshooting

### Agent fails with "GOOGLE_API_KEY not found"
- Ensure `.env` exists and contains `GOOGLE_API_KEY=...`
- In CI, add `GOOGLE_API_KEY` to GitHub repo secrets

### Agent fails with "unrecognized arguments: --mode ci"
- Fixed in latest. Ensure `main.py` includes `--mode` argument.

### Trivy fails the build
- Fix CRITICAL/HIGH vulnerabilities or add to `.trivyignore`
- Or temporarily set `exit-code: "0"` in CI (not recommended)

### Provider returns empty/mock logs
- **GitHub**: Ensure `build_logs.txt` exists (artifact download) or pass `--logs` directly
- **Jenkins**: Set JENKINS_URL, JENKINS_USER, JENKINS_TOKEN
- **AWS**: Configure AWS credentials (env, ~/.aws, IAM role) and pass CodeBuild build ID
- **Azure**: Set AZURE_DEVOPS_ORG, AZURE_DEVOPS_PROJECT, AZURE_DEVOPS_PAT

### Dashboard shows "Status file not found"
- Run the agent at least once (local mode) to generate `status.json`
- Or ensure `src/dashboard/public/status.json` exists

### Audit log not found
- Agent writes to `logs/agent_audit.jsonl`. Create `logs/` if needed.
- Set `AUDIT_DISABLED=1` to disable audit logging.
