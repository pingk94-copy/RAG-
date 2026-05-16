from __future__ import annotations

from dataclasses import dataclass
import re

from rag.hybrid_retriever import HybridSearchResult


@dataclass(frozen=True)
class RerankedResult:
    chunk: object
    retrieval_score: float
    rerank_score: float
    sources: tuple[str, ...]


class SimpleReranker:
    """Lightweight reranker based on query-context token overlap."""

    def rerank(
        self,
        query: str,
        candidates: list[HybridSearchResult],
        top_k: int = 5,
    ) -> list[RerankedResult]:
        query_tokens = set(_tokenize(query))
        reranked: list[RerankedResult] = []

        for candidate in candidates:
            content_tokens = set(_tokenize(candidate.chunk.content))
            overlap = query_tokens & content_tokens
            overlap_score = len(overlap) / len(query_tokens) if query_tokens else 0.0
            score = overlap_score + candidate.score
            reranked.append(
                RerankedResult(
                    chunk=candidate.chunk,
                    retrieval_score=candidate.score,
                    rerank_score=score,
                    sources=candidate.sources,
                )
            )

        reranked.sort(key=lambda item: item.rerank_score, reverse=True)
        return reranked[:top_k]


def _tokenize(text: str) -> list[str]:
    raw_tokens = re.findall(r"[A-Za-z0-9_-]+|[\u4e00-\u9fff]+", text.lower())
    tokens: list[str] = []
    stopwords = {"的", "了", "和", "是", "吗", "什么", "怎么", "可以", "哪些"}
    for token in raw_tokens:
        if re.fullmatch(r"[\u4e00-\u9fff]+", token):
            tokens.extend(char for char in token if char not in stopwords)
            tokens.extend(token[index : index + 2] for index in range(len(token) - 1))
        elif token not in stopwords:
            tokens.append(token)
    return tokens
