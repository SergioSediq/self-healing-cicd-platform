# Contributing to Self-Healing CI/CD Platform

## Development Setup

1. Clone the repo and install dependencies:
   ```bash
   pip install -r src/agent/requirements.txt -r src/agent/requirements-test.txt
   cd src/dashboard && npm install
   ```

2. Copy `.env.example` to `.env` and set `GOOGLE_API_KEY`.

3. Run pre-commit (optional):
   ```bash
   pip install pre-commit && pre-commit install
   ```

## Adding a New CI Provider

1. Edit `src/agent/lib/providers.py`
2. Create a class extending `CIProvider` with:
   - `fetch_logs(run_id: str) -> str`
   - `get_context() -> str`
   - `validate_env() -> tuple[bool, str]`
3. Register in `get_provider()`.
4. Add tests in `src/agent/tests/test_providers.py`.
5. Document in `INTEGRATIONS.md` and `.env.example`.

## Running Tests

```bash
# Agent (pytest)
cd src/agent && python -m pytest tests/ -v -k "not e2e"

# Dashboard (Jest)
cd src/dashboard && npm test
```

## Code Style

- Python: Black (line length 100)
- TypeScript: ESLint + Prettier

## Submitting Changes

1. Create a branch from `main`
2. Run tests and pre-commit
3. Open a Pull Request with a clear description
