from __future__ import annotations

import argparse
from pathlib import Path

from rag.ingest import build_chunks, load_documents
from rag.simple_rag import SimpleRAG


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

    rag = SimpleRAG()
    rag.add_chunks(chunks)

    result = rag.ask(args.question)
    print(result.answer)
    if result.sources:
        print("\nSources:")
        for source in result.sources:
            print(f"- {source.document_name}#chunk-{source.chunk_id} score={source.score:.2f}")


if __name__ == "__main__":
    main()
