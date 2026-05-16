from __future__ import annotations

from dataclasses import dataclass
import re

from rag.chunker import chunk_text
from rag.ingest import KnowledgeChunk


@dataclass(frozen=True)
class Source:
    document_name: str
    chunk_id: int
    content: str
    score: float


@dataclass(frozen=True)
class Answer:
    answer: str
    sources: list[Source]


class SimpleRAG:
    """A dependency-light RAG pipeline for validating the first iteration."""

    def __init__(self, chunk_size: int = 300, overlap: int = 40) -> None:
        self.chunk_size = chunk_size
        self.overlap = overlap
        self._sources: list[Source] = []

    def add_document(self, document_name: str, text: str) -> None:
        for chunk_id, chunk in enumerate(
            chunk_text(text, chunk_size=self.chunk_size, overlap=self.overlap)
        ):
            self._sources.append(
                Source(
                    document_name=document_name,
                    chunk_id=chunk_id,
                    content=chunk,
                    score=0.0,
                )
            )

    def add_chunks(self, chunks: list[KnowledgeChunk]) -> None:
        for chunk in chunks:
            location = f"p{chunk.page_number}"
            if chunk.heading:
                location = f"{location} {chunk.heading}"
            self._sources.append(
                Source(
                    document_name=chunk.document_name,
                    chunk_id=chunk.chunk_id,
                    content=f"[{location}]\n{chunk.content}",
                    score=0.0,
                )
            )

    def ask(self, question: str, top_k: int = 3) -> Answer:
        matches = self.retrieve(question, top_k=top_k)
        if not matches:
            return Answer(answer="资料中没有找到明确依据。", sources=[])

        best = matches[0]
        return Answer(answer=best.content, sources=matches)

    def retrieve(self, question: str, top_k: int = 3) -> list[Source]:
        query_terms = set(_tokenize(question))
        if not query_terms:
            return []

        scored: list[Source] = []
        for source in self._sources:
            content_terms = set(_tokenize(source.content))
            overlap = query_terms & content_terms
            if not overlap:
                continue
            score = len(overlap) / len(query_terms)
            scored.append(
                Source(
                    document_name=source.document_name,
                    chunk_id=source.chunk_id,
                    content=source.content,
                    score=score,
                )
            )

        scored.sort(key=lambda item: item.score, reverse=True)
        return scored[:top_k]


def _tokenize(text: str) -> list[str]:
    words = re.findall(r"[A-Za-z0-9_]+|[\u4e00-\u9fff]", text.lower())
    stopwords = {"的", "了", "和", "是", "吗", "什么", "怎么", "可以", "支持"}
    return [word for word in words if word not in stopwords]
