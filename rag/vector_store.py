from __future__ import annotations

from dataclasses import dataclass

from rag.embeddings import EmbeddingModel
from rag.ingest import KnowledgeChunk


@dataclass(frozen=True)
class VectorSearchResult:
    chunk: KnowledgeChunk
    score: float


@dataclass(frozen=True)
class _StoredVector:
    chunk: KnowledgeChunk
    vector: list[float]


class InMemoryVectorStore:
    """Small vector-store adapter with the same shape expected from remote stores."""

    def __init__(self, embedding_model: EmbeddingModel) -> None:
        self.embedding_model = embedding_model
        self._items: list[_StoredVector] = []

    def add(self, chunks: list[KnowledgeChunk]) -> None:
        for chunk in chunks:
            self._items.append(
                _StoredVector(
                    chunk=chunk,
                    vector=self.embedding_model.embed(chunk.content),
                )
            )

    def search(self, query: str, top_k: int = 5) -> list[VectorSearchResult]:
        if top_k <= 0:
            return []

        query_vector = self.embedding_model.embed(query)
        scored = [
            VectorSearchResult(chunk=item.chunk, score=_cosine_similarity(query_vector, item.vector))
            for item in self._items
        ]
        scored = [item for item in scored if item.score > 0]
        scored.sort(key=lambda item: item.score, reverse=True)
        return scored[:top_k]

    def clear(self) -> None:
        self._items.clear()


def _cosine_similarity(left: list[float], right: list[float]) -> float:
    return sum(a * b for a, b in zip(left, right))
