# 🏗 Architecture & Flow Diagram

This document illustrates the autonomous self-healing workflow of the platform.

```mermaid
graph LR
    %% Styles
    classDef user fill:#1e293b,stroke:#94a3b8,stroke-width:2px,color:#fff
    classDef ci fill:#2563eb,stroke:#3b82f6,stroke-width:2px,color:#fff
    classDef ai fill:#7c3aed,stroke:#8b5cf6,stroke-width:2px,color:#fff
    classDef infra fill:#059669,stroke:#10b981,stroke-width:2px,color:#fff
    classDef fail stroke:#ef4444,stroke-width:2px,fill:#fecaca,color:#991b1b
    classDef success stroke:#10b981,stroke-width:2px,fill:#d1fae5,color:#065f46

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

    %% Apply Styles
    class Dev,Repo user
    class JobTest,Deploy,Artifact,HealJob ci
    class Agent,Gemini,FixCode ai
    class K8s infra
```

## 🔄 Workflow Logic

1. **Code Push**: Developer pushes code to the repository.
2. **Standard Pipeline**: The CI runs "Build & Test".
    * ✅ **If Pass**: Continues to Deployment.
    * ❌ **If Fail**: Stops standard flow, uploads logs, and triggers the **Auto-Heal Job**.
3. **AI Analysis**: The Auto-Heal job activates the **AI Agent**, which:
    * Reads the failure logs.
    * Sends them to **Gemini 3 Pro** for deep reasoning.
    * Identifies the exact file and code causing the crash.
4. **Automatic Repair**: The Agent rewrites the broken code in the file system.
5. **Loop Closure**: The Agent pushes the fix back to the repo, automatically triggering a new pipeline run to verify the fix.
