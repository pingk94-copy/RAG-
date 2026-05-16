from __future__ import annotations

from dataclasses import dataclass
import hashlib
import math
import re
from typing import Protocol


class EmbeddingModel(Protocol):
    def embed(self, text: str) -> list[float]:
        """Convert text into a vector."""


@dataclass(frozen=True)
class HashingEmbeddingModel:
    """Deterministic local embedding model used until a real model is wired in."""

    dimensions: int = 256

    def embed(self, text: str) -> list[float]:
        if self.dimensions <= 0:
            raise ValueError("dimensions must be positive")

        vector = [0.0] * self.dimensions
        for token in _tokenize(text):
            digest = hashlib.sha256(token.encode("utf-8")).digest()
            index = int.from_bytes(digest[:4], "big") % self.dimensions
            sign = 1.0 if digest[4] % 2 == 0 else -1.0
            vector[index] += sign

        return _normalize(vector)


def create_embedding_model(config: dict[str, object] | None = None) -> EmbeddingModel:
    settings = config or {}
    provider = str(settings.get("provider", "hashing")).lower()
    if provider == "hashing":
        dimensions = int(settings.get("dimensions", 256))
        return HashingEmbeddingModel(dimensions=dimensions)
    raise ValueError(f"Unsupported embedding provider: {provider}")


def _tokenize(text: str) -> list[str]:
    raw_tokens = re.findall(r"[A-Za-z0-9_]+|[\u4e00-\u9fff]+", text.lower())
    tokens: list[str] = []
    for token in raw_tokens:
        if re.fullmatch(r"[\u4e00-\u9fff]+", token):
            tokens.extend(token)
            tokens.extend(token[index : index + 2] for index in range(len(token) - 1))
        else:
            tokens.append(token)
    return tokens


def _normalize(vector: list[float]) -> list[float]:
    norm = math.sqrt(sum(value * value for value in vector))
    if norm == 0:
        return vector
    return [value / norm for value in vector]
