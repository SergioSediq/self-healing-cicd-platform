"""Alternate prompts for recovery when primary analysis fails."""

RECOVERY_PROMPT = """You are a DevOps expert. The build failed. Analyze these logs briefly.

LOGS:
{logs}

Respond with:
1. ROOT_CAUSE: one sentence
2. FIX: what to change
3. FILE: which file to edit
4. CONFIDENCE: 0.0 to 1.0
"""
