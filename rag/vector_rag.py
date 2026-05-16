from __future__ import annotations

from dataclasses import dataclass

from rag.ingest import KnowledgeChunk
from rag.vector_store import InMemoryVectorStore


@dataclass(frozen=True)
class VectorAnswer:
    answer: str
    sources: list[KnowledgeChunk]


class VectorRAG:
    def __init__(self, vector_store: InMemoryVectorStore) -> None:
        self.vector_store = vector_store

    def ask(self, question: str, top_k: int = 3) -> VectorAnswer:
        results = self.vector_store.search(question, top_k=top_k)
        if not results:
            return VectorAnswer(answer="资料中没有找到明确依据。", sources=[])

        best = results[0].chunk
        return VectorAnswer(
            answer=best.content,
            sources=[result.chunk for result in results],
        )
