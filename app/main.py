from __future__ import annotations

from fastapi import FastAPI
from pydantic import BaseModel, Field

from rag.service import IngestedDocument, RAGService


app = FastAPI(title="RAG 智能问答 API")
service = RAGService()


class DocumentInput(BaseModel):
    name: str
    content: str
    kind: str = "txt"


class IngestRequest(BaseModel):
    documents: list[DocumentInput] = Field(default_factory=list)


class IngestResponse(BaseModel):
    documents: int
    chunks: int


class AskRequest(BaseModel):
    question: str


class SourceResponse(BaseModel):
    document_name: str
    page_number: int
    heading: str | None
    chunk_id: int
    content: str


class AskResponse(BaseModel):
    answer: str
    citations: list[str]
    sources: list[SourceResponse]


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


@app.post("/ingest", response_model=IngestResponse)
def ingest(request: IngestRequest) -> IngestResponse:
    summary = service.ingest_documents(
        [
            IngestedDocument(name=document.name, content=document.content, kind=document.kind)
            for document in request.documents
        ]
    )
    return IngestResponse(documents=summary.documents, chunks=summary.chunks)


@app.post("/ask", response_model=AskResponse)
def ask(request: AskRequest) -> AskResponse:
    answer = service.ask(request.question)
    return AskResponse(
        answer=answer.answer,
        citations=answer.citations,
        sources=[
            SourceResponse(
                document_name=source.document_name,
                page_number=source.page_number,
                heading=source.heading,
                chunk_id=source.chunk_id,
                content=source.content,
            )
            for source in answer.sources
        ],
    )
