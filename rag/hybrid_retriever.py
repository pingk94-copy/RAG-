from __future__ import annotations

from dataclasses import dataclass

from rag.ingest import KnowledgeChunk
from rag.keyword_retriever import BM25Retriever
from rag.vector_store import InMemoryVectorStore


@dataclass(frozen=True)
class HybridSearchResult:
    chunk: KnowledgeChunk
    score: float
    sources: tuple[str, ...]


class HybridRetriever:
    def __init__(
        self,
        vector_store: InMemoryVectorStore,
        keyword_retriever: BM25Retriever,
        rank_constant: int = 60,
    ) -> None:
        self.vector_store = vector_store
        self.keyword_retriever = keyword_retriever
        self.rank_constant = rank_constant
        self._chunks_by_id: dict[int, KnowledgeChunk] = {}

    def add(self, chunks: list[KnowledgeChunk]) -> None:
        self.vector_store.add(chunks)
        self.keyword_retriever.add(chunks)
        self._chunks_by_id.update({chunk.chunk_id: chunk for chunk in chunks})

    def search(self, query: str, top_k: int = 5) -> list[HybridSearchResult]:
        vector_results = self.vector_store.search(query, top_k=top_k)
        keyword_results = self.keyword_retriever.search(query, top_k=top_k)
        ranked_lists = [
            [("vector", result.chunk.chunk_id) for result in vector_results],
            [("keyword", result.chunk.chunk_id) for result in keyword_results],
        ]
        fused = reciprocal_rank_fusion(ranked_lists, rank_constant=self.rank_constant)

        source_names_by_chunk: dict[int, set[str]] = {}
        for source_name, chunk_id in ranked_lists[0] + ranked_lists[1]:
            source_names_by_chunk.setdefault(chunk_id, set()).add(source_name)

        results: list[HybridSearchResult] = []
        for chunk_id, score in fused[:top_k]:
            chunk = self._chunks_by_id.get(chunk_id)
            if chunk is None:
                continue
            results.append(
                HybridSearchResult(
                    chunk=chunk,
                    score=score,
                    sources=tuple(sorted(source_names_by_chunk.get(chunk_id, set()))),
                )
            )
        return results

    def clear(self) -> None:
        self.vector_store.clear()
        self.keyword_retriever.clear()
        self._chunks_by_id.clear()


def reciprocal_rank_fusion(
    ranked_lists: list[list[tuple[str, int]]],
    rank_constant: int = 60,
) -> list[tuple[int, float]]:
    scores: dict[int, float] = {}
    for ranked_list in ranked_lists:
        for rank, (_source_name, chunk_id) in enumerate(ranked_list, start=1):
            scores[chunk_id] = scores.get(chunk_id, 0.0) + 1.0 / (rank_constant + rank)

    return sorted(scores.items(), key=lambda item: item[1], reverse=True)
