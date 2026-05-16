from __future__ import annotations

import argparse
from pathlib import Path

from rag.answer_generator import AnswerGenerator
from rag.embeddings import HashingEmbeddingModel
from rag.hybrid_retriever import HybridRetriever
from rag.ingest import build_chunks, load_documents
from rag.keyword_retriever import BM25Retriever
from rag.reranker import SimpleReranker
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
    retrieved = retriever.search(args.question, top_k=5)
    reranked = SimpleReranker().rerank(args.question, retrieved, top_k=3)
    answer = AnswerGenerator().generate(args.question, reranked)

    print(answer.answer)
    if answer.citations:
        print("\nCitations:")
        for citation in answer.citations:
            print(f"- {citation}")

    if reranked:
        print("\nRetrieved:")
        for result in reranked:
            source = result.chunk
            paths = ",".join(result.sources)
            print(
                f"- {source.document_name}#chunk-{source.chunk_id} "
                f"page={source.page_number} via={paths} "
                f"rerank={result.rerank_score:.4f}"
            )


if __name__ == "__main__":
    main()
