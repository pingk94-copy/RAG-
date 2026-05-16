import pytest

from rag.embeddings import HashingEmbeddingModel, create_embedding_model
from rag.qdrant_store import QdrantVectorStore
from rag.service import RAGService


def test_create_embedding_model_defaults_to_hashing():
    model = create_embedding_model({"provider": "hashing", "dimensions": 32})

    vector = model.embed("产品说明书")

    assert isinstance(model, HashingEmbeddingModel)
    assert len(vector) == 32


def test_create_embedding_model_rejects_unknown_provider():
    with pytest.raises(ValueError, match="Unsupported embedding provider"):
        create_embedding_model({"provider": "unknown"})


def test_qdrant_store_requires_optional_dependency_when_missing():
    with pytest.raises(RuntimeError, match="qdrant-client"):
        QdrantVectorStore.from_config(
            embedding_model=HashingEmbeddingModel(dimensions=16),
            config={"url": "http://localhost:6333", "collection": "rag_test"},
        )


def test_rag_service_accepts_vector_backend_config():
    service = RAGService(
        embedding_config={"provider": "hashing", "dimensions": 32},
        vector_store_config={"provider": "memory"},
    )
    summary = service.ingest_documents(
        [
            {
                "name": "manual.txt",
                "content": "系统支持上传产品说明书。",
                "kind": "txt",
            }
        ]
    )

    answer = service.ask("系统支持上传什么？")

    assert summary.chunks == 1
    assert "产品说明书" in answer.answer
