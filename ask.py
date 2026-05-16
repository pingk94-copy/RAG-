from __future__ import annotations

import argparse
from pathlib import Path

from rag.document_loader import LoadedDocument
from rag.ingest import load_documents
from rag.service import IngestedDocument, RAGService


def main() -> None:
    parser = argparse.ArgumentParser(description="Ask a question against local text files.")
    parser.add_argument("question", help="Question to ask")
    parser.add_argument(
        "--docs",
        default="data/raw",
        help="Directory containing .txt or .md documents",
    )
    args = parser.parse_args()

    docs_dir = Path(args.docs)
    documents = load_documents(docs_dir)
    service = RAGService()
    service.ingest_documents([_to_ingested_document(document) for document in documents])
    answer = service.ask(args.question)

    print(answer.answer)
    if answer.citations:
        print("\nCitations:")
        for citation in answer.citations:
            print(f"- {citation}")

    if answer.sources:
        print("\nSources:")
        for source in answer.sources:
            heading = f" heading={source.heading}" if source.heading else ""
            print(f"- {source.document_name}#chunk-{source.chunk_id} page={source.page_number}{heading}")


def _to_ingested_document(document: LoadedDocument) -> IngestedDocument:
    content = "\n\n".join(page.text for page in document.pages)
    return IngestedDocument(name=document.name, content=content, kind=document.kind)


if __name__ == "__main__":
    main()
