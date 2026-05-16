from __future__ import annotations

import argparse
from pathlib import Path

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

    rag = SimpleRAG()
    docs_dir = Path(args.docs)
    for path in sorted(docs_dir.glob("*")):
        if path.suffix.lower() not in {".txt", ".md"}:
            continue
        rag.add_document(path.name, path.read_text(encoding="utf-8"))

    result = rag.ask(args.question)
    print(result.answer)
    if result.sources:
        print("\nSources:")
        for source in result.sources:
            print(f"- {source.document_name}#chunk-{source.chunk_id} score={source.score:.2f}")


if __name__ == "__main__":
    main()
