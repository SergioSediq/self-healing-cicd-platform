# 🤖 Autonomous Self-Healing CI/CD Platform

> **🛡️ Enterprise-grade AIOps platform for autonomous infrastructure and code remediation.**

---

## 📋 Overview

When a pipeline fails (build error, test failure), the AI Agent automatically:

| Step | Action | Description |
|------|--------|-------------|
| 1️⃣ | **Detect** | Identifies the failure from CI logs |
| 2️⃣ | **Analyze** | Uses Google Gemini to diagnose root cause |
| 3️⃣ | **Propose** | Suggests code or config fixes with confidence scores |
| 4️⃣ | **Implement** | Applies the fix and commits to a new branch |
| 5️⃣ | **Retry** | Triggers a new pipeline run to verify the fix |

💡 *Low confidence? The agent requests human review instead of auto-applying.*  

---

## 🏗️ Architecture & Flow Diagram

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

## 🛠️ Tech Stack

| Layer | Technology | Purpose |
|-------|------------|---------|
| 🧠 **AI Agent** | Python, LangChain, Google Gemini | Log analysis, root-cause inference, fix generation |
| ⚙️ **CI/CD** | GitHub Actions, Jenkins, AWS, Azure, GitLab | Pipeline integration |
| ☸️ **Infrastructure** | Kubernetes (Kind), Terraform, Docker | Target deployment |
| 📊 **Dashboard** | Next.js, TailwindCSS | Observability UI |
| 📈 **Observability** | OpenTelemetry, Prometheus | SLOs, metrics, tracing |

---

## 🗣️ Languages

| Language | Used In |
|----------|---------|
| **Python** | AI agent, LangChain workflows |
| **TypeScript / JavaScript** | Next.js dashboard |
| **HCL** | Terraform infrastructure |
| **YAML** | Kubernetes manifests, GitHub Actions, Helm |

---

## 📁 Project Structure

```
├── src/agent/           🧠 Python AI agent (LangChain + Gemini)
├── src/dashboard/       📊 Next.js observability UI
├── src/target_app/      🎯 Demo application for testing
├── infra/               ☸️ Terraform, K8s manifests, Helm
├── docs/                📚 Runbooks, ADRs, guides
└── .github/workflows/   ⚙️ CI pipeline definitions
```

---

## 🚀 Quick Start

```bash
# 1. Configure secrets
cp .env.example .env   # Add GOOGLE_API_KEY, GITHUB_TOKEN

# 2. Run the AI agent (dry-run)
cd src/agent && pip install -r requirements.txt
python main.py --provider local --dry-run

# 3. Launch the dashboard
cd src/dashboard && npm install && npm run dev
```

📖 **Further reading:** [docs/SETUP_RUNBOOK.md](docs/SETUP_RUNBOOK.md) · [INTEGRATIONS.md](INTEGRATIONS.md)

---

## 👤 Author

**Sergio Sediq**

- 🔗 [GitHub](https://github.com/SergioSediq)
- 💼 [LinkedIn](https://www.linkedin.com/in/sedyagho/)
- ✉️ sediqsergio@gmail.com
