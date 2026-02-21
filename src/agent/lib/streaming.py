"""Streaming LLM responses for incremental output."""
import json
from typing import Iterator

from langchain_core.output_parsers import PydanticOutputParser
from langchain_core.prompts import PromptTemplate
from pydantic import BaseModel


def stream_analysis_chunks(prompt, llm, parser, inputs: dict) -> Iterator[str]:
    """Stream raw text chunks from LLM. Caller must assemble/parse."""
    chain = prompt | llm
    for chunk in chain.stream(inputs):
        if hasattr(chunk, "content") and chunk.content:
            yield chunk.content
        elif isinstance(chunk, str):
            yield chunk


def parse_streamed_result(accumulated: str, parser: PydanticOutputParser, model: type) -> BaseModel | None:
    """Try to parse accumulated stream into Pydantic model."""
    try:
        return parser.parse(accumulated)
    except Exception:
        return None
