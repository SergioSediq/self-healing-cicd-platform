# Autonomous Self-Healing CI/CD Platform

**Enterprise-grade AIOps platform for autonomous infrastructure and code remediation.**

---

## Overview

When a pipeline fails (build error, test failure), the AI Agent:

1. **Detects** the failure  
2. **Analyzes** logs using Google Gemini  
3. **Proposes** a fix (code or config)  
4. **Implements** the fix via commit/PR  
5. **Retries** the pipeline upon approval  

---

## Architecture & Flow Diagram

```mermaid
graph LR
    classDef user fill:#1e293b,stroke:#94a3b8,stroke-width:2px,color:#fff
    classDef ci fill:#2563eb,stroke:#3b82f6,stroke-width:2px,color:#fff
    classDef ai fill:#7c3aed,stroke:#8b5cf6,stroke-width:2px,color:#fff
    classDef infra fill:#059669,stroke:#10b981,stroke-width:2px,color:#fff

    subgraph User_Zone [👩‍💻 Developer]
        Dev([Developer]) -->|Push Code| Repo[GitHub Repo]
    end

    subgraph CI_CD [⚙️ CI/CD Pipeline]
        Repo -->|Trigger| JobTest{Build & Test}
        JobTest -->|Pass| Deploy[Deploy Stage]
        JobTest -- Fail --> Artifact[Upload Logs]
        Artifact --> HealJob[🤖 Auto-Heal Job]
    end

    subgraph AI_Core [🧠 AI Healing Brain]
        HealJob -->|Fetch Logs| Agent[Python Agent]
        Agent -->|Analyze| Gemini[Google Gemini 3 Pro]
        Gemini -->|Root Cause & Fix| Agent
        Agent -->|Generate Fix| FixCode[Fixed File]
    end

    subgraph Resolution [🔄 Self-Correction]
        FixCode -->|Commit & Push| PR[New Branch/PR]
        PR -.->|Trigger New Run| JobTest
    end

    subgraph Target [🚀 Infrastructure]
        Deploy -->|Update| K8s[Kubernetes Cluster]
    end

    class Dev,Repo user
    class JobTest,Deploy,Artifact,HealJob ci
    class Agent,Gemini,FixCode ai
    class K8s infra
```

---

## Tech Stack

| Layer        | Technology                          |
| ------------ | ----------------------------------- |
| **AI Agent** | Python, LangChain, Google Gemini    |
| **CI/CD**    | GitHub Actions, Jenkins, AWS, Azure, GitLab |
| **Infrastructure** | Kubernetes (Kind), Terraform, Docker |
| **Dashboard** | Next.js, TailwindCSS                |
| **Observability** | OpenTelemetry, Prometheus          |

---

## Project Structure

```
├── src/agent/        # Python AI agent (LangChain + Gemini)
├── src/dashboard/    # Next.js observability UI
├── src/target_app/   # Demo application for testing
├── infra/            # Terraform, K8s manifests, Helm
├── docs/             # Runbooks, ADRs, guides
└── .github/workflows/ # CI pipeline
```

---

## Quick Start

```bash
cp .env.example .env   # Add GOOGLE_API_KEY, GITHUB_TOKEN
cd src/agent && pip install -r requirements.txt
python main.py --provider local --dry-run
cd src/dashboard && npm install && npm run dev
```

See [docs/SETUP_RUNBOOK.md](docs/SETUP_RUNBOOK.md) and [INTEGRATIONS.md](INTEGRATIONS.md).

---

## Author

**Sergio Sediq**

- GitHub: [@SergioSediq](https://github.com/SergioSediq)
- LinkedIn: [Sergio Sediq](https://www.linkedin.com/in/sedyagho/)
- Email: sediqsergio@gmail.com
