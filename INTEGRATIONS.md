# 🔌 Integrations & Roadmap

This platform is designing to be **agnostic** to the CI/CD provider and Deployment target.

## Supported Providers

| Provider | Status | Integration Method |
| :--- | :--- | :--- |
| **GitHub Actions** | ✅ Active | Uses `GITHUB_TOKEN` to read build logs/artifacts. |
| **Jenkins** | ✅ Active | Connects via Jenkins API to fetch `consoleText` of failed builds. |
| **AWS CodePipeline** | ✅ Active | Fetches CloudWatch Logs for CodeBuild execution via boto3. |
| **Azure DevOps** | ✅ Active | Reads Pipeline Run logs via Azure DevOps REST API. |
| **Local / Docker** | ✅ Active | Reads local file logs (Demo Mode). |

## 🏗 Modular Architecture

The agent uses a **Provider Interface** (`src/agent/lib/providers.py`) to abstract the difference between CI tools.

### 1. The Provider Interface

Every integration implements this simple contract:

```python
class CIProvider(ABC):
    @abstractmethod
    def fetch_logs(self, run_id: str) -> str:
        pass
```

### 2. How to add a new Provider (e.g. GitLab CI)

1. Create a class in `src/agent/lib/providers.py`:

    ```python
    class GitLabProvider(CIProvider):
        def fetch_logs(self, job_id):
            return requests.get(f"https://gitlab.com/api/v4/projects/{id}/jobs/{job_id}/trace").text
    ```

2. Register it in the `get_provider()` factory.
3. Run the agent with `--provider gitlab`.

## 🚀 Deployment Targets

The Agent creates **Code Fixes** (GitOps approach). It does not SSH into servers to fix things.
This means it supports **ANY** deployment target that is managed by code:

* **Kubernetes**: Agent fixes `k8s/*.yaml` or Helm Charts.
* **Docker / ECS**: Agent fixes `Dockerfile` (as seen in demo).
* **Terraform / CloudFormation**: Agent fixes `.tf` files for Infrastructure failures.
* **Serverless**: Agent fixes `serverless.yml` or `SAM` templates.

The "Deployment Target" is transparent to the agent; it just heals the *Source of Truth* (The Code).

## Per-Provider Setup

### Jenkins
- **JENKINS_URL**: Base URL (e.g. `https://jenkins.example.com`)
- **JENKINS_USER**: Jenkins username
- **JENKINS_TOKEN**: API token (Manage Jenkins → Credentials)
- **run_id**: Use `jobname/build_number` or `folder/jobname/build_number`

### AWS CodePipeline / CodeBuild
- **AWS credentials**: Env vars, `~/.aws/credentials`, or IAM role
- **AWS_REGION**: Region (default: us-east-1)
- **run_id**: CodeBuild build ID (e.g. `my-project:abc123`)

### Azure DevOps
- **AZURE_DEVOPS_ORG**: Organization name
- **AZURE_DEVOPS_PROJECT**: Project name
- **AZURE_DEVOPS_PAT**: Personal Access Token (Pipelines read)
- **run_id**: Pipeline run ID (integer)
