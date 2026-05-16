from rag.answer_generator import AnswerGenerator
from rag.hybrid_retriever import HybridSearchResult
from rag.ingest import KnowledgeChunk
from rag.reranker import SimpleReranker


def _result(chunk_id: int, content: str, score: float = 0.02) -> HybridSearchResult:
    return HybridSearchResult(
        chunk=KnowledgeChunk(
            document_name="manual.txt",
            document_kind="txt",
            page_number=chunk_id + 1,
            heading="使用说明",
            chunk_id=chunk_id,
            content=content,
        ),
        score=score,
        sources=("keyword", "vector"),
    )


def test_simple_reranker_prefers_more_query_overlap():
    reranker = SimpleReranker()
    candidates = [
        _result(0, "设备支持蓝牙连接。"),
        _result(1, "系统支持上传产品说明书和技术文档。"),
    ]

    reranked = reranker.rerank("可以上传什么文档？", candidates, top_k=2)

    assert reranked[0].chunk.chunk_id == 1
    assert reranked[0].rerank_score > reranked[1].rerank_score


def test_answer_generator_returns_answer_with_citations():
    generator = AnswerGenerator(min_score=0.1)
    candidates = [
        _result(0, "系统支持上传产品说明书和技术文档。", score=0.03),
    ]
    reranked = SimpleReranker().rerank("系统支持上传什么？", candidates)

    answer = generator.generate("系统支持上传什么？", reranked)

    assert "产品说明书" in answer.answer
    assert answer.citations == ["manual.txt p1 使用说明 #0"]
    assert answer.sources[0].chunk_id == 0


def test_answer_generator_refuses_low_confidence_context():
    generator = AnswerGenerator(min_score=0.9)
    candidates = [
        _result(0, "设备支持蓝牙连接。", score=0.01),
    ]
    reranked = SimpleReranker().rerank("天气怎么样？", candidates)

    answer = generator.generate("天气怎么样？", reranked)

    assert answer.answer == "资料中没有找到明确依据。"
    assert answer.citations == []
    assert answer.sources == []
