# Fine-Tuning Guide (Future)

To fine-tune on your failure/fix history:

1. Export feedback: `GET /api/export-audit?format=json` and filter by `fix_applied`
2. Use `logs/feedback.jsonl` for thumbs up/down signals
3. Prepare training data: (logs, analysis, fix) triples
4. Use Google Vertex AI or similar for Gemini fine-tuning

See [feedback loop documentation] for data format.
