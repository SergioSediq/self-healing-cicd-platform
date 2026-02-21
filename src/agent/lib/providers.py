"""Multi-cloud CI/CD provider implementations."""
from abc import ABC, abstractmethod
import base64
import os
import requests
from typing import Optional

# Optional imports for providers that need extra deps
try:
    import boto3
    from botocore.exceptions import ClientError
    HAS_BOTO3 = True
except ImportError:
    HAS_BOTO3 = False


class CIProvider(ABC):
    """Abstract Base Class for CI/CD Providers."""

    @abstractmethod
    def fetch_logs(self, run_id: str) -> str:
        """Fetches build/deployment logs for a specific run ID."""
        pass

    @abstractmethod
    def get_context(self) -> str:
        """Returns metadata about the environment (e.g. 'Jenkins Job: Payment-API')."""
        pass

    @abstractmethod
    def validate_env(self) -> tuple[bool, str]:
        """Returns (is_valid, error_message). Override to validate provider-specific env vars."""
        return True, ""


class LocalProvider(CIProvider):
    """Used for local simulation/demo."""

    def fetch_logs(self, run_id: str) -> str:
        print(f"[*] (Local) Returning mock logs for {run_id}")
        return """
        Step 4/5 : RUN npm test
        > target-app@1.0.0 test
        > node test.js

        Running comprehensive test suite...
        Checking environment configuration...
        ❌ CRITICAL ERROR: Environment variable 'FIX_APPLIED' is missing.
        Test suite failed.
        npm ERR! Test failed.
        """

    def get_context(self) -> str:
        return "Local Docker Environment"

    def validate_env(self) -> tuple[bool, str]:
        return True, ""


class GitHubActionsProvider(CIProvider):
    """Integration for GitHub Actions."""

    def __init__(self):
        self.token = os.getenv("GITHUB_TOKEN")
        self.repo = os.getenv("GITHUB_REPOSITORY", "user/repo")

    def fetch_logs(self, run_id: str) -> str:
        if not self.token:
            return "❌ Error: GITHUB_TOKEN not set."

        print(f"[*] (GitHub) Fetching logs for run {run_id} from {self.repo}")

        # In CI, logs are usually in build_logs.txt after artifact download
        if os.path.exists("build_logs.txt"):
            with open("build_logs.txt", "r", encoding="utf-8", errors="replace") as f:
                return f.read()

        # Fallback: try GitHub API for job logs (requires run_id as job run ID)
        try:
            owner, repo_name = self.repo.split("/", 1)
            url = f"https://api.github.com/repos/{owner}/{repo_name}/actions/jobs/{run_id}/logs"
            headers = {
                "Authorization": f"Bearer {self.token}",
                "Accept": "application/vnd.github+json",
                "X-GitHub-Api-Version": "2022-11-28",
            }
            resp = requests.get(url, headers=headers, timeout=30)
            if resp.status_code == 200:
                return resp.text
            return f"Error: GitHub API returned {resp.status_code}. build_logs.txt not found."
        except Exception as e:
            return f"Error fetching GitHub logs: {e}"

    def get_context(self) -> str:
        return f"GitHub Actions ({self.repo})"

    def validate_env(self) -> tuple[bool, str]:
        if not self.token:
            return False, "GITHUB_TOKEN is required for GitHub provider"
        return True, ""


class JenkinsProvider(CIProvider):
    """Integration for Jenkins via REST API."""

    def __init__(self):
        self.url = (os.getenv("JENKINS_URL") or "").rstrip("/")
        self.user = os.getenv("JENKINS_USER")
        self.token = os.getenv("JENKINS_TOKEN")

    def fetch_logs(self, run_id: str) -> str:
        if not self.url:
            return "❌ Error: JENKINS_URL not set."

        # run_id can be "jobname/123" or "folder/jobname/123"
        job_path = run_id.replace("/", "/job/")
        console_url = f"{self.url}/job/{job_path}/consoleText"

        print(f"[*] (Jenkins) Fetching console output from {console_url}")

        try:
            auth = (self.user, self.token) if self.user and self.token else None
            resp = requests.get(console_url, auth=auth, timeout=60)
            resp.raise_for_status()
            return resp.text
        except requests.RequestException as e:
            return f"❌ Jenkins API error: {e}"

    def get_context(self) -> str:
        return f"Jenkins Host: {self.url}"

    def validate_env(self) -> tuple[bool, str]:
        if not self.url:
            return False, "JENKINS_URL is required for Jenkins provider"
        if not self.user or not self.token:
            return False, "JENKINS_USER and JENKINS_TOKEN are required for Jenkins API auth"
        return True, ""


class AWSCodePipelineProvider(CIProvider):
    """Integration for AWS CodePipeline / CodeBuild via boto3."""

    def __init__(self):
        self.region = os.getenv("AWS_REGION", "us-east-1")
        self._client = None

    def _get_client(self):
        if self._client is None and HAS_BOTO3:
            self._client = boto3.client("codebuild", region_name=self.region)
        return self._client

    def fetch_logs(self, run_id: str) -> str:
        if not HAS_BOTO3:
            return "❌ Error: boto3 not installed. Run: pip install boto3"

        client = self._get_client()
        if not client:
            return "❌ Error: Could not create CodeBuild client. Check AWS credentials."

        print(f"[*] (AWS) Fetching CodeBuild logs for build ID {run_id}")

        try:
            build = client.batch_get_builds(ids=[run_id])
            builds = build.get("builds", [])
            if not builds:
                return f"❌ No build found for ID: {run_id}"

            b = builds[0]

            # Get CloudWatch log group/stream from build
            log_info = b.get("logs", {})
            log_group = log_info.get("groupName")
            log_stream = log_info.get("streamName")

            if not log_group or not log_stream:
                return f"❌ Build {run_id} has no associated logs. Status: {b.get('buildStatus', 'unknown')}"

            logs_client = boto3.client("logs", region_name=self.region)
            response = logs_client.get_log_events(
                logGroupName=log_group,
                logStreamName=log_stream,
                startFromHead=True,
            )
            events = response.get("events", [])
            return "\n".join(e.get("message", "") for e in events)
        except ClientError as e:
            return f"❌ AWS API error: {e}"
        except Exception as e:
            return f"❌ Error fetching AWS logs: {e}"

    def get_context(self) -> str:
        return f"AWS CodePipeline (region: {self.region})"

    def validate_env(self) -> tuple[bool, str]:
        if not HAS_BOTO3:
            return False, "boto3 is required for AWS provider. Install with: pip install boto3"
        # AWS uses default credential chain (env, ~/.aws/credentials, IAM role)
        return True, ""


class AzureDevOpsProvider(CIProvider):
    """Integration for Azure DevOps Pipelines via REST API."""

    def __init__(self):
        self.org = os.getenv("AZURE_DEVOPS_ORG")
        self.project = os.getenv("AZURE_DEVOPS_PROJECT")
        self.pat = os.getenv("AZURE_DEVOPS_PAT")

    def fetch_logs(self, run_id: str) -> str:
        if not self.org or not self.project or not self.pat:
            return "❌ Error: AZURE_DEVOPS_ORG, AZURE_DEVOPS_PROJECT, AZURE_DEVOPS_PAT must be set."

        # run_id can be pipeline run ID (integer)
        base = f"https://dev.azure.com/{self.org}/{self.project}/_apis"
        headers = {
            "Authorization": "Basic " + base64.b64encode(f":{self.pat}".encode()).decode().strip(),
            "Content-Type": "application/json",
        }

        print(f"[*] (Azure) Fetching pipeline logs for run {run_id}")

        try:
            # Get timeline (jobs/steps) for the run
            url = f"{base}/build/builds/{run_id}/timeline?api-version=7.1"
            r = requests.get(url, headers=headers, timeout=30)
            r.raise_for_status()
            timeline = r.json()
            records = timeline.get("records", [])

            log_lines = []
            for rec in records:
                log_lines.append(f"[{rec.get('recordType', '')}] {rec.get('name', '')}: {rec.get('state', '')} - {rec.get('result', '')}")

            # Try to get build logs if available
            url2 = f"{base}/build/builds/{run_id}/logs?api-version=7.1"
            r2 = requests.get(url2, headers=headers, timeout=30)
            if r2.status_code == 200:
                logs_meta = r2.json()
                for log in logs_meta.get("value", [])[:5]:
                    log_id = log.get("id")
                    log_url = f"{base}/build/builds/{run_id}/logs/{log_id}?api-version=7.1"
                    r3 = requests.get(log_url, headers=headers, timeout=30)
                    if r3.status_code == 200:
                        log_content = r3.text
                        log_lines.append(f"\n--- Log {log.get('type', '')} ---\n{log_content}")

            return "\n".join(log_lines) if log_lines else f"Run {run_id} timeline retrieved but no log content."
        except requests.RequestException as e:
            return f"❌ Azure DevOps API error: {e}"
        except Exception as e:
            return f"❌ Error fetching Azure logs: {e}"

    def get_context(self) -> str:
        return f"Azure DevOps ({self.org}/{self.project})"

    def validate_env(self) -> tuple[bool, str]:
        if not self.org:
            return False, "AZURE_DEVOPS_ORG is required"
        if not self.project:
            return False, "AZURE_DEVOPS_PROJECT is required"
        if not self.pat:
            return False, "AZURE_DEVOPS_PAT is required for Azure DevOps API"
        return True, ""


class GitLabProvider(CIProvider):
    """Integration for GitLab CI."""

    def __init__(self):
        self.token = os.getenv("GITLAB_TOKEN")
        self.base = (os.getenv("GITLAB_URL") or "https://gitlab.com").rstrip("/")

    def fetch_logs(self, run_id: str) -> str:
        if not self.token:
            return "❌ Error: GITLAB_TOKEN not set."
        project_id = os.getenv("CI_PROJECT_ID", "").replace("/", "%2F")
        job_id = run_id if run_id.isdigit() else ""
        if not project_id or not job_id:
            return "❌ GITLAB: Set CI_PROJECT_ID and pass job id as run_id."
        url = f"{self.base}/api/v4/projects/{project_id}/jobs/{job_id}/trace"
        headers = {"PRIVATE-TOKEN": self.token}
        try:
            r = requests.get(url, headers=headers, timeout=60)
            r.raise_for_status()
            return r.text
        except requests.RequestException as e:
            return f"❌ GitLab API error: {e}"

    def get_context(self) -> str:
        return f"GitLab CI ({self.base})"

    def validate_env(self) -> tuple[bool, str]:
        if not self.token:
            return False, "GITLAB_TOKEN is required"
        return True, ""


def get_provider(provider_name: str) -> CIProvider:
    """Returns a CIProvider instance for the given provider name."""
    mapping = {
        "local": LocalProvider,
        "github": GitHubActionsProvider,
        "jenkins": JenkinsProvider,
        "aws": AWSCodePipelineProvider,
        "azure": AzureDevOpsProvider,
        "gitlab": GitLabProvider,
    }
    return mapping.get((provider_name or "").lower(), LocalProvider)()
