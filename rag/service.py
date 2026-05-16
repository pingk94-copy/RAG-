from __future__ import annotations

from dataclasses import dataclass

from rag.answer_generator import AnswerGenerator, GeneratedAnswer
from rag.document_loader import DocumentPage, DocumentSection, LoadedDocument
from rag.embeddings import HashingEmbeddingModel
from rag.hybrid_retriever import HybridRetriever
from rag.ingest import KnowledgeChunk, build_chunks
from rag.keyword_retriever import BM25Retriever
from rag.reranker import SimpleReranker
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
    def __init__(self) -> None:
        self._chunks: list[KnowledgeChunk] = []
        self._reset_retriever()

    def ingest_documents(self, documents: list[IngestedDocument]) -> IngestSummary:
        loaded_documents = [_to_loaded_document(document) for document in documents]
        chunks = build_chunks(loaded_documents)
        self._chunks = chunks
        self._reset_retriever()
        self._retriever.add(chunks)
        return IngestSummary(documents=len(loaded_documents), chunks=len(chunks))

    def ask(self, question: str) -> GeneratedAnswer:
        retrieved = self._retriever.search(question, top_k=5)
        reranked = SimpleReranker().rerank(question, retrieved, top_k=3)
        return AnswerGenerator().generate(question, reranked)

    def _reset_retriever(self) -> None:
        self._retriever = HybridRetriever(
            vector_store=InMemoryVectorStore(HashingEmbeddingModel()),
            keyword_retriever=BM25Retriever(),
        )


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
