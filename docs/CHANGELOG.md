# Changelog

All notable changes to the Self-Healing CI/CD Platform.

## [Unreleased]

### Added
- Streaming LLM responses
- Async providers with httpx
- Quorum for fixes (multiple runs must agree)
- Undo/redo (rollback_n)
- Pre-apply verification
- Recovery mode prompts
- Web UI theme toggle (dark/light)
- Fix preview / diff API
- Feedback widget (thumbs up/down)
- Cost dashboard API
- Audit export (CSV/JSON)
- Secret detection in output
- Feature flags
- Rate limiting middleware
- Slack, Teams, Discord, Jira integrations

### Changed
- Status API returns cache headers
- History API supports pagination and retention

### Deprecated
- (none)

### Removed
- (none)

### Security
- Secret detection blocks sensitive content in fixes
- Rate limiting on API routes
