# Canary Deployments

For gradual rollout of agent versions:

1. Deploy new agent version to a canary pool (e.g. 10% of workers)
2. Route 10% of jobs to canary via queue tagging
3. Compare success rate: canary vs stable
4. Promote canary to 100% if metrics are good
5. Rollback by routing all traffic back to stable

Implement with Kubernetes multiple deployments + weighted routing.
