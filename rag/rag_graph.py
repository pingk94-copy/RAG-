from __future__ import annotations

from dataclasses import dataclass, field

from rag.answer_generator import AnswerGenerator, GeneratedAnswer
from rag.hybrid_retriever import HybridRetriever, HybridSearchResult
from rag.reranker import RerankedResult, SimpleReranker
from rag.safety import SAFETY_REFUSAL, SafetyChecker


@dataclass
class RAGGraphState:
    question: str
    executed_nodes: list[str] = field(default_factory=list)
    blocked: bool = False
    retrieved: list[HybridSearchResult] = field(default_factory=list)
    reranked: list[RerankedResult] = field(default_factory=list)
    answer: GeneratedAnswer | None = None


class RAGGraph:
    """Explicit graph-style orchestration for the RAG pipeline."""

    def __init__(
        self,
        retriever: HybridRetriever,
        reranker: SimpleReranker,
        answer_generator: AnswerGenerator,
        safety_checker: SafetyChecker,
    ) -> None:
        self.retriever = retriever
        self.reranker = reranker
        self.answer_generator = answer_generator
        self.safety_checker = safety_checker

    def run(self, question: str) -> RAGGraphState:
        state = RAGGraphState(question=question)
        self._safety_node(state)
        if state.blocked:
            return state

        self._retrieve_node(state)
        self._rerank_node(state)
        self._generate_node(state)
        return state

    def _safety_node(self, state: RAGGraphState) -> None:
        state.executed_nodes.append("safety")
        decision = self.safety_checker.check_question(state.question)
        if not decision.allowed:
            state.blocked = True
            state.answer = GeneratedAnswer(answer=SAFETY_REFUSAL, citations=[], sources=[])

    def _retrieve_node(self, state: RAGGraphState) -> None:
        state.executed_nodes.append("retrieve")
        state.retrieved = self.retriever.search(state.question, top_k=5)

    def _rerank_node(self, state: RAGGraphState) -> None:
        state.executed_nodes.append("rerank")
        state.reranked = self.reranker.rerank(state.question, state.retrieved, top_k=3)

    def _generate_node(self, state: RAGGraphState) -> None:
        state.executed_nodes.append("generate")
        state.answer = self.answer_generator.generate(state.question, state.reranked)
