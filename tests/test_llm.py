from types import SimpleNamespace

from rag.answer_generator import AnswerGenerator
from rag.hybrid_retriever import HybridSearchResult
from rag.ingest import KnowledgeChunk
from rag.llm import OpenAIResponsesLLMClient, create_llm_client_from_env
from rag.reranker import SimpleReranker


class FakeResponses:
    def __init__(self) -> None:
        self.request = None

    def create(self, **kwargs):
        self.request = kwargs
        return SimpleNamespace(output_text="根据资料，系统支持上传产品说明书和技术文档。")


class FakeOpenAIClient:
    def __init__(self) -> None:
        self.responses = FakeResponses()


def _candidate() -> HybridSearchResult:
    return HybridSearchResult(
        chunk=KnowledgeChunk(
            document_name="manual.txt",
            document_kind="txt",
            page_number=1,
            heading=None,
            chunk_id=0,
            content="系统支持上传产品说明书和技术文档。",
        ),
        score=0.02,
        sources=("keyword", "vector"),
    )


def test_openai_responses_client_uses_responses_api():
    fake_client = FakeOpenAIClient()
    client = OpenAIResponsesLLMClient(
        api_key="test-key",
        base_url="https://api.openai.com/v1",
        model="gpt-4.1-mini",
        client=fake_client,
    )

    text = client.generate_answer("系统支持上传什么？", ["系统支持上传产品说明书和技术文档。"])

    assert "产品说明书" in text
    assert fake_client.responses.request["model"] == "gpt-4.1-mini"
    assert "系统支持上传什么？" in fake_client.responses.request["input"]


def test_create_llm_client_from_env_returns_none_without_key(tmp_path):
    env_path = tmp_path / ".env"
    env_path.write_text("OPENAI_MODEL=gpt-4.1-mini\n", encoding="utf-8")

    assert create_llm_client_from_env(env_path) is None


def test_answer_generator_uses_llm_when_available():
    fake_client = FakeOpenAIClient()
    llm = OpenAIResponsesLLMClient(
        api_key="test-key",
        base_url=None,
        model="gpt-4.1-mini",
        client=fake_client,
    )
    contexts = SimpleReranker().rerank("系统支持上传什么？", [_candidate()])

    answer = AnswerGenerator(llm_client=llm).generate("系统支持上传什么？", contexts)

    assert answer.answer == "根据资料，系统支持上传产品说明书和技术文档。"
    assert answer.citations == ["manual.txt p1 #0"]


def test_answer_generator_falls_back_without_llm():
    contexts = SimpleReranker().rerank("系统支持上传什么？", [_candidate()])

    answer = AnswerGenerator().generate("系统支持上传什么？", contexts)

    assert answer.answer == "系统支持上传产品说明书和技术文档。"
