from __future__ import annotations

import argparse
from pathlib import Path

from rag.embeddings import HashingEmbeddingModel
from rag.hybrid_retriever import HybridRetriever
from rag.ingest import build_chunks, load_documents
from rag.keyword_retriever import BM25Retriever
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

    retriever = HybridRetriever(
        vector_store=InMemoryVectorStore(HashingEmbeddingModel()),
        keyword_retriever=BM25Retriever(),
    )
    retriever.add(chunks)
    results = retriever.search(args.question, top_k=3)

    if not results:
        print("资料中没有找到明确依据。")
    else:
        print(results[0].chunk.content)
        print("\nSources:")
        for result in results:
            source = result.chunk
            heading = f" heading={source.heading}" if source.heading else ""
            paths = ",".join(result.sources)
            print(
                f"- {source.document_name}#chunk-{source.chunk_id} "
                f"page={source.page_number}{heading} via={paths} rrf={result.score:.4f}"
            )


if __name__ == "__main__":
    main()
