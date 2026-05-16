from rag.chunker import chunk_text
from rag.simple_rag import SimpleRAG


def test_chunk_text_splits_with_overlap():
    chunks = chunk_text("abcdefghijklmnopqrstuvwxyz", chunk_size=10, overlap=2)

    assert chunks == [
        "abcdefghij",
        "ijklmnopqr",
        "qrstuvwxyz",
    ]


def test_simple_rag_returns_answer_and_sources():
    rag = SimpleRAG()
    rag.add_document(
        "manual.txt",
        "产品支持智能问答。系统可以上传说明书，并基于说明书内容回答用户问题。",
    )

    result = rag.ask("系统可以上传什么？")

    assert "说明书" in result.answer
    assert result.sources
    assert result.sources[0].document_name == "manual.txt"


def test_simple_rag_refuses_when_no_context_matches():
    rag = SimpleRAG()
    rag.add_document("manual.txt", "设备支持蓝牙连接和电量显示。")

    result = rag.ask("今天西安天气怎么样？")

    assert result.answer == "资料中没有找到明确依据。"
    assert result.sources == []
