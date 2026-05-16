from rag.embeddings import HashingEmbeddingModel
from rag.ingest import KnowledgeChunk
from rag.vector_rag import VectorRAG
from rag.vector_store import InMemoryVectorStore


def test_hashing_embedding_model_returns_stable_normalized_vectors():
    model = HashingEmbeddingModel(dimensions=16)

    first = model.embed("产品说明书支持上传")
    second = model.embed("产品说明书支持上传")

    assert first == second
    assert len(first) == 16
    assert round(sum(value * value for value in first), 6) == 1.0


def test_vector_store_returns_relevant_chunks_with_metadata():
    model = HashingEmbeddingModel(dimensions=32)
    store = InMemoryVectorStore(model)
    chunks = [
        KnowledgeChunk(
            document_name="manual.txt",
            document_kind="txt",
            page_number=1,
            heading="上传",
            chunk_id=0,
            content="系统支持上传产品说明书和技术文档。",
        ),
        KnowledgeChunk(
            document_name="manual.txt",
            document_kind="txt",
            page_number=1,
            heading="连接",
            chunk_id=1,
            content="设备支持蓝牙连接和电量显示。",
        ),
    ]

    store.add(chunks)
    results = store.search("可以上传什么文档？", top_k=1)

    assert len(results) == 1
    assert results[0].chunk.content == "系统支持上传产品说明书和技术文档。"
    assert results[0].chunk.heading == "上传"
    assert results[0].score > 0


def test_vector_store_can_be_cleared():
    model = HashingEmbeddingModel(dimensions=16)
    store = InMemoryVectorStore(model)
    store.add(
        [
            KnowledgeChunk(
                document_name="manual.txt",
                document_kind="txt",
                page_number=1,
                heading=None,
                chunk_id=0,
                content="系统支持上传产品说明书。",
            )
        ]
    )

    store.clear()

    assert store.search("上传", top_k=1) == []


def test_vector_rag_answers_with_vector_search_sources():
    model = HashingEmbeddingModel(dimensions=32)
    store = InMemoryVectorStore(model)
    store.add(
        [
            KnowledgeChunk(
                document_name="manual.txt",
                document_kind="txt",
                page_number=2,
                heading="文档上传",
                chunk_id=7,
                content="系统可以上传产品说明书、技术文档和常见问题文件。",
            )
        ]
    )
    rag = VectorRAG(store)

    answer = rag.ask("系统能上传哪些文档？")

    assert "产品说明书" in answer.answer
    assert answer.sources[0].document_name == "manual.txt"
    assert answer.sources[0].page_number == 2
    assert answer.sources[0].heading == "文档上传"
