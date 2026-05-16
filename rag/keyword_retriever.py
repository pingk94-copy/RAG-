from __future__ import annotations

from dataclasses import dataclass
import math
import re

from rag.ingest import KnowledgeChunk


@dataclass(frozen=True)
class KeywordSearchResult:
    chunk: KnowledgeChunk
    score: float


class BM25Retriever:
    def __init__(self, k1: float = 1.5, b: float = 0.75) -> None:
        self.k1 = k1
        self.b = b
        self._chunks: list[KnowledgeChunk] = []
        self._tokenized_docs: list[list[str]] = []
        self._doc_freq: dict[str, int] = {}
        self._avg_doc_length = 0.0

    def add(self, chunks: list[KnowledgeChunk]) -> None:
        for chunk in chunks:
            tokens = _tokenize(chunk.content)
            self._chunks.append(chunk)
            self._tokenized_docs.append(tokens)
            for token in set(tokens):
                self._doc_freq[token] = self._doc_freq.get(token, 0) + 1

        total_length = sum(len(tokens) for tokens in self._tokenized_docs)
        self._avg_doc_length = total_length / len(self._tokenized_docs) if self._tokenized_docs else 0.0

    def search(self, query: str, top_k: int = 5) -> list[KeywordSearchResult]:
        if top_k <= 0 or not self._chunks:
            return []

        query_tokens = _tokenize(query)
        scored: list[KeywordSearchResult] = []
        for chunk, doc_tokens in zip(self._chunks, self._tokenized_docs):
            score = self._score(query_tokens, doc_tokens)
            if score > 0:
                scored.append(KeywordSearchResult(chunk=chunk, score=score))

        scored.sort(key=lambda item: item.score, reverse=True)
        return scored[:top_k]

    def clear(self) -> None:
        self._chunks.clear()
        self._tokenized_docs.clear()
        self._doc_freq.clear()
        self._avg_doc_length = 0.0

    def _score(self, query_tokens: list[str], doc_tokens: list[str]) -> float:
        if not doc_tokens or self._avg_doc_length == 0:
            return 0.0

        token_counts: dict[str, int] = {}
        for token in doc_tokens:
            token_counts[token] = token_counts.get(token, 0) + 1

        score = 0.0
        doc_count = len(self._tokenized_docs)
        doc_length = len(doc_tokens)
        for token in query_tokens:
            term_frequency = token_counts.get(token, 0)
            if term_frequency == 0:
                continue
            doc_frequency = self._doc_freq.get(token, 0)
            idf = math.log(1 + (doc_count - doc_frequency + 0.5) / (doc_frequency + 0.5))
            numerator = term_frequency * (self.k1 + 1)
            denominator = term_frequency + self.k1 * (
                1 - self.b + self.b * doc_length / self._avg_doc_length
            )
            score += idf * numerator / denominator

        return score


def _tokenize(text: str) -> list[str]:
    raw_tokens = re.findall(r"[A-Za-z0-9_-]+|[\u4e00-\u9fff]+", text.lower())
    tokens: list[str] = []
    stopwords = {"的", "了", "和", "是", "吗", "什么", "怎么", "可以"}
    for token in raw_tokens:
        if re.fullmatch(r"[\u4e00-\u9fff]+", token):
            tokens.extend(char for char in token if char not in stopwords)
            tokens.extend(token[index : index + 2] for index in range(len(token) - 1))
        elif token not in stopwords:
            tokens.append(token)
    return tokens
