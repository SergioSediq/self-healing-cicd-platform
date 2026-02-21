"""RAG stub: retrieve docs for context. Extend with vector DB (Chroma, Pinecone)."""
import os
from pathlib import Path

DOCS_DIR = Path(os.getenv("RAG_DOCS_DIR", "docs"))


def get_relevant_docs(query: str, top_k: int = 3) -> str:
    """
    Stub: return static docs. Replace with vector search over embedded docs.
    """
    if not DOCS_DIR.exists():
        return ""
    snippets = []
    for f in DOCS_DIR.rglob("*.md"):
        try:
            text = f.read_text(encoding="utf-8", errors="ignore")
            if query.lower() in text.lower():
                snippets.append(text[:500] + "..." if len(text) > 500 else text)
                if len(snippets) >= top_k:
                    break
        except Exception:
            pass
    return "\n\n---\n\n".join(snippets) if snippets else ""
