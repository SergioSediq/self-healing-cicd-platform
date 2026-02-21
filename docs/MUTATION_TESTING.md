# Mutation Testing

Use `mutmut` to assess test quality:

```bash
pip install mutmut
cd src/agent
mutmut run
mutmut results
```

Mutants that survive indicate missing test coverage.
