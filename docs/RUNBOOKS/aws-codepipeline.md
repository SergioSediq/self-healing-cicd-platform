# AWS CodePipeline Runbook

## Setup
- AWS credentials (env, ~/.aws, or IAM role)
- `AWS_REGION` (default: us-east-1)
- run_id = CodeBuild build ID

## Common Issues
| Symptom | Cause | Fix |
|---------|-------|-----|
| No build found | Wrong build ID | Use full build ID from CodeBuild console |
| Access denied | IAM permissions | Add `codebuild:BatchGetBuilds`, `logs:GetLogEvents` |
| No logs | Build in progress | Wait for build to complete |
