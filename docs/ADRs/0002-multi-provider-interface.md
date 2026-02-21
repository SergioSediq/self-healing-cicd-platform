# ADR 0002: Multi-Provider CI Interface

## Status
Accepted

## Context
Different teams use different CI systems (GitHub Actions, Jenkins, AWS, Azure). The agent must fetch logs from any of them.

## Decision
Define an abstract `CIProvider` interface with `fetch_logs` and `get_context`. Implement providers for each platform. Use `get_provider(name)` factory.

## Consequences
- Easy to add GitLab, CircleCI, etc.
- Provider-specific env validation
- Clean separation of concerns
