from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from rag.embeddings import EmbeddingModel
from rag.ingest import KnowledgeChunk
from rag.vector_store import VectorSearchResult


@dataclass(frozen=True)
class QdrantConfig:
    url: str = "http://localhost:6333"
    collection: str = "rag_chunks"
    vector_size: int = 256


class QdrantVectorStore:
    """Qdrant adapter kept optional so local tests work without a running service."""

    def __init__(self, client: Any, embedding_model: EmbeddingModel, config: QdrantConfig) -> None:
        self.client = client
        self.embedding_model = embedding_model
        self.config = config

    @classmethod
    def from_config(
        cls,
        embedding_model: EmbeddingModel,
        config: dict[str, object] | None = None,
    ) -> "QdrantVectorStore":
        try:
            from qdrant_client import QdrantClient  # type: ignore
        except ImportError as exc:
            raise RuntimeError(
                "Qdrant backend requires optional dependency qdrant-client. "
                "Install it with: pip install qdrant-client"
            ) from exc

        settings = config or {}
        qdrant_config = QdrantConfig(
            url=str(settings.get("url", "http://localhost:6333")),
            collection=str(settings.get("collection", "rag_chunks")),
            vector_size=int(settings.get("vector_size", 256)),
        )
        client = QdrantClient(url=qdrant_config.url)
        return cls(client=client, embedding_model=embedding_model, config=qdrant_config)

    def add(self, chunks: list[KnowledgeChunk]) -> None:
        try:
            from qdrant_client.models import PointStruct, VectorParams, Distance  # type: ignore
        except ImportError as exc:
            raise RuntimeError("qdrant-client is required for Qdrant operations") from exc

        self.client.recreate_collection(
            collection_name=self.config.collection,
            vectors_config=VectorParams(size=self.config.vector_size, distance=Distance.COSINE),
        )
        points = [
            PointStruct(
                id=chunk.chunk_id,
                vector=self.embedding_model.embed(chunk.content),
                payload={
                    "document_name": chunk.document_name,
                    "document_kind": chunk.document_kind,
                    "page_number": chunk.page_number,
                    "heading": chunk.heading,
                    "chunk_id": chunk.chunk_id,
                    "content": chunk.content,
                },
            )
            for chunk in chunks
        ]
        if points:
            self.client.upsert(collection_name=self.config.collection, points=points)

    def search(self, query: str, top_k: int = 5) -> list[VectorSearchResult]:
        query_vector = self.embedding_model.embed(query)
        hits = self.client.search(
            collection_name=self.config.collection,
            query_vector=query_vector,
            limit=top_k,
        )
        results: list[VectorSearchResult] = []
        for hit in hits:
            payload = hit.payload or {}
            chunk = KnowledgeChunk(
                document_name=str(payload.get("document_name", "")),
                document_kind=str(payload.get("document_kind", "")),
                page_number=int(payload.get("page_number", 1)),
                heading=payload.get("heading"),
                chunk_id=int(payload.get("chunk_id", hit.id)),
                content=str(payload.get("content", "")),
            )
            results.append(VectorSearchResult(chunk=chunk, score=float(hit.score)))
        return results

    def clear(self) -> None:
        self.client.delete_collection(collection_name=self.config.collection)
