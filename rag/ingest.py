from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from rag.chunker import chunk_text
from rag.document_loader import LoadedDocument, load_document


@dataclass(frozen=True)
class KnowledgeChunk:
    document_name: str
    document_kind: str
    page_number: int
    heading: str | None
    chunk_id: int
    content: str


def load_documents(directory: str | Path, strict: bool = False) -> list[LoadedDocument]:
    docs_dir = Path(directory)
    supported = {".txt", ".md", ".pdf"}
    documents: list[LoadedDocument] = []
    for path in sorted(docs_dir.glob("*")):
        if path.is_file() and path.suffix.lower() in supported:
            try:
                documents.append(load_document(path))
            except Exception:
                if strict:
                    raise
    return documents


def build_chunks(
    documents: list[LoadedDocument],
    chunk_size: int = 500,
    overlap: int = 50,
) -> list[KnowledgeChunk]:
    chunks: list[KnowledgeChunk] = []

    for document in documents:
        for page in document.pages:
            for section in page.sections:
                for content in chunk_text(section.text, chunk_size=chunk_size, overlap=overlap):
                    chunks.append(
                        KnowledgeChunk(
                            document_name=document.name,
                            document_kind=document.kind,
                            page_number=page.page_number,
                            heading=section.heading,
                            chunk_id=len(chunks),
                            content=content,
                        )
                    )

    return chunks
