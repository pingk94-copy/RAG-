from __future__ import annotations

import argparse
from pathlib import Path

from rag.embeddings import HashingEmbeddingModel
from rag.ingest import build_chunks, load_documents
from rag.vector_rag import VectorRAG
from rag.vector_store import InMemoryVectorStore


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
    chunks = build_chunks(documents)

    vector_store = InMemoryVectorStore(HashingEmbeddingModel())
    vector_store.add(chunks)
    rag = VectorRAG(vector_store)

    result = rag.ask(args.question)
    print(result.answer)
    if result.sources:
        print("\nSources:")
        for source in result.sources:
            heading = f" heading={source.heading}" if source.heading else ""
            print(
                f"- {source.document_name}#chunk-{source.chunk_id} "
                f"page={source.page_number}{heading}"
            )


if __name__ == "__main__":
    main()
