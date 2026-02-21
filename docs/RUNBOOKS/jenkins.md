# Jenkins Runbook

## Setup
- `JENKINS_URL`, `JENKINS_USER`, `JENKINS_TOKEN` must be set
- run_id format: `jobname/build_number` or `folder/jobname/build_number`

## Common Issues
| Symptom | Cause | Fix |
|---------|-------|-----|
| 401 Unauthorized | Invalid credentials | Regenerate API token |
| 404 | Wrong job path | Use full path: folder/job/123 |
| Empty logs | Job not finished | Ensure build completed |
