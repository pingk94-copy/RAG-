from __future__ import annotations

import argparse
from pathlib import Path

from rag.ingest import build_chunks, load_documents


def main() -> None:
    parser = argparse.ArgumentParser(description="Preview parsed document chunks.")
    parser.add_argument(
        "--docs",
        default="data/raw",
        help="Directory containing .txt, .md or .pdf documents",
    )
    parser.add_argument("--chunk-size", type=int, default=500)
    parser.add_argument("--overlap", type=int, default=50)
    args = parser.parse_args()

    documents = load_documents(Path(args.docs))
    chunks = build_chunks(documents, chunk_size=args.chunk_size, overlap=args.overlap)

    print(f"documents={len(documents)} chunks={len(chunks)}")
    for chunk in chunks:
        heading = chunk.heading or "-"
        preview = chunk.content.replace("\n", " ")[:80]
        print(
            f"- #{chunk.chunk_id} {chunk.document_name} "
            f"page={chunk.page_number} heading={heading} text={preview}"
        )


if __name__ == "__main__":
    main()
