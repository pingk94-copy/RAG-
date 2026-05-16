from __future__ import annotations

from dataclasses import dataclass

from rag.ingest import KnowledgeChunk
from rag.reranker import RerankedResult


@dataclass(frozen=True)
class GeneratedAnswer:
    answer: str
    citations: list[str]
    sources: list[KnowledgeChunk]


class AnswerGenerator:
    """Extractive answer generator used before wiring in an LLM."""

    def __init__(self, min_score: float = 0.05, max_sources: int = 3) -> None:
        self.min_score = min_score
        self.max_sources = max_sources

    def generate(self, question: str, contexts: list[RerankedResult]) -> GeneratedAnswer:
        relevant = [context for context in contexts if context.rerank_score >= self.min_score]
        if not relevant:
            return GeneratedAnswer(answer="资料中没有找到明确依据。", citations=[], sources=[])

        selected = relevant[: self.max_sources]
        answer = selected[0].chunk.content
        sources = [context.chunk for context in selected]
        citations = [_format_citation(source) for source in sources]

        return GeneratedAnswer(answer=answer, citations=citations, sources=sources)


def _format_citation(source: KnowledgeChunk) -> str:
    heading = f" {source.heading}" if source.heading else ""
    return f"{source.document_name} p{source.page_number}{heading} #{source.chunk_id}"
