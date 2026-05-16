from __future__ import annotations

from dataclasses import dataclass

from rag.answer_generator import AnswerGenerator, GeneratedAnswer
from rag.document_loader import DocumentPage, DocumentSection, LoadedDocument
from rag.embeddings import create_embedding_model
from rag.hybrid_retriever import HybridRetriever
from rag.ingest import KnowledgeChunk, build_chunks
from rag.keyword_retriever import BM25Retriever
from rag.llm import create_llm_client_from_env
from rag.qdrant_store import QdrantVectorStore
from rag.rag_graph import RAGGraph
from rag.reranker import SimpleReranker
from rag.safety import SafetyChecker
from rag.vector_store import InMemoryVectorStore


@dataclass(frozen=True)
class IngestedDocument:
    name: str
    content: str
    kind: str = "txt"


@dataclass(frozen=True)
class IngestSummary:
    documents: int
    chunks: int


class RAGService:
    def __init__(
        self,
        embedding_config: dict[str, object] | None = None,
        vector_store_config: dict[str, object] | None = None,
    ) -> None:
        self.embedding_config = embedding_config or {"provider": "hashing"}
        self.vector_store_config = vector_store_config or {"provider": "memory"}
        self._chunks: list[KnowledgeChunk] = []
        self.reranker = SimpleReranker()
        self.answer_generator = AnswerGenerator(llm_client=create_llm_client_from_env())
        self.safety_checker = SafetyChecker()
        self._reset_retriever()

    def ingest_documents(self, documents: list[IngestedDocument | dict[str, str]]) -> IngestSummary:
        loaded_documents = [_to_loaded_document(_coerce_document(document)) for document in documents]
        chunks = build_chunks(loaded_documents)
        self._chunks = chunks
        self._reset_retriever()
        self._retriever.add(chunks)
        return IngestSummary(documents=len(loaded_documents), chunks=len(chunks))

    def ask(self, question: str) -> GeneratedAnswer:
        state = RAGGraph(
            retriever=self.retriever,
            reranker=self.reranker,
            answer_generator=self.answer_generator,
            safety_checker=self.safety_checker,
        ).run(question)
        assert state.answer is not None
        return state.answer

    @property
    def retriever(self):
        return self._retriever

    def _reset_retriever(self) -> None:
        embedding_model = create_embedding_model(self.embedding_config)
        self._retriever = HybridRetriever(
            vector_store=_create_vector_store(embedding_model, self.vector_store_config),
            keyword_retriever=BM25Retriever(),
        )


def _coerce_document(document: IngestedDocument | dict[str, str]) -> IngestedDocument:
    if isinstance(document, IngestedDocument):
        return document
    return IngestedDocument(
        name=document["name"],
        content=document["content"],
        kind=document.get("kind", "txt"),
    )


def _create_vector_store(embedding_model, config: dict[str, object]):
    provider = str(config.get("provider", "memory")).lower()
    if provider == "memory":
        return InMemoryVectorStore(embedding_model)
    if provider == "qdrant":
        return QdrantVectorStore.from_config(embedding_model=embedding_model, config=config)
    raise ValueError(f"Unsupported vector store provider: {provider}")


def _to_loaded_document(document: IngestedDocument) -> LoadedDocument:
    page = DocumentPage(
        page_number=1,
        text=document.content,
        sections=[DocumentSection(heading=None, text=document.content)],
    )
    return LoadedDocument(
        name=document.name,
        kind=document.kind,
        path=document.name,
        pages=[page],
    )
