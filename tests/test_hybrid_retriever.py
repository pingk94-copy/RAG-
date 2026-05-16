from rag.embeddings import HashingEmbeddingModel
from rag.hybrid_retriever import HybridRetriever, reciprocal_rank_fusion
from rag.ingest import KnowledgeChunk
from rag.keyword_retriever import BM25Retriever
from rag.vector_store import InMemoryVectorStore


def _chunk(chunk_id: int, content: str, heading: str | None = None) -> KnowledgeChunk:
    return KnowledgeChunk(
        document_name="manual.txt",
        document_kind="txt",
        page_number=1,
        heading=heading,
        chunk_id=chunk_id,
        content=content,
    )


def test_bm25_retriever_matches_exact_product_model():
    retriever = BM25Retriever()
    retriever.add(
        [
            _chunk(0, "设备型号 AX-900 支持蓝牙连接。"),
            _chunk(1, "系统支持上传产品说明书。"),
        ]
    )

    results = retriever.search("AX-900 怎么连接？", top_k=1)

    assert len(results) == 1
    assert results[0].chunk.chunk_id == 0
    assert results[0].score > 0


def test_reciprocal_rank_fusion_combines_ranked_lists():
    fused = reciprocal_rank_fusion(
        ranked_lists=[
            [("vector", 1), ("vector", 2)],
            [("keyword", 2), ("keyword", 3)],
        ],
        rank_constant=60,
    )

    assert fused[0][0] == 2
    assert {chunk_id for chunk_id, _score in fused} == {1, 2, 3}


def test_hybrid_retriever_fuses_vector_and_keyword_results():
    chunks = [
        _chunk(0, "设备型号 AX-900 支持蓝牙连接。", heading="型号"),
        _chunk(1, "系统支持上传产品说明书和技术文档。", heading="上传"),
    ]
    vector_store = InMemoryVectorStore(HashingEmbeddingModel(dimensions=64))
    keyword_retriever = BM25Retriever()
    retriever = HybridRetriever(vector_store=vector_store, keyword_retriever=keyword_retriever)
    retriever.add(chunks)

    results = retriever.search("AX-900 怎么连接？", top_k=2)

    assert results
    assert results[0].chunk.chunk_id == 0
    assert results[0].sources
    assert "keyword" in results[0].sources or "vector" in results[0].sources
