# A/B Testing Models

To compare models or prompts:

1. Set `LLM_PRIMARY_MODEL` and `LLM_FALLBACK_MODEL` per run
2. Use `FEATURE_AB_MODEL_A` / `FEATURE_AB_MODEL_B` (future)
3. Track outcomes in `logs/token_usage.jsonl` and `logs/feedback.jsonl`
4. Compare heal success rate by model via cost dashboard
