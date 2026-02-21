# ADR 0001: Use LangChain for LLM Integration

## Status
Accepted

## Context
The agent needs to call LLM APIs (Google Gemini) for log analysis and code fix generation. We needed a consistent way to structure prompts and parse outputs.

## Decision
Use LangChain with `langchain-google-genai` for:
- Prompt templates
- Pydantic output parsing
- Model abstraction (primary/fallback)

## Consequences
- Structured, testable prompt logic
- Easy to add new models or providers
- Dependency on LangChain ecosystem
