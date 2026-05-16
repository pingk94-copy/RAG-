from __future__ import annotations

from dataclasses import dataclass
import argparse
import json
from pathlib import Path
import sys

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from rag.service import IngestedDocument, RAGService


REFUSAL_ANSWER = "资料中没有找到明确依据。"


@dataclass(frozen=True)
class EvaluationCase:
    question: str
    documents: list[dict[str, str]]
    expected_keywords: list[str]
    should_refuse: bool = False


@dataclass(frozen=True)
class EvaluationResult:
    question: str
    answer: str
    expected_keywords: list[str]
    matched_keywords: list[str]
    should_refuse: bool
    refused: bool
    passed: bool


@dataclass(frozen=True)
class EvaluationReport:
    total: int
    passed: int
    keyword_hit_rate: float
    refusal_accuracy: float
    results: list[EvaluationResult]


def evaluate_cases(cases: list[EvaluationCase]) -> EvaluationReport:
    results = [_evaluate_case(case) for case in cases]
    total = len(results)
    passed = sum(1 for result in results if result.passed)

    keyword_cases = [result for result in results if not result.should_refuse]
    keyword_hit_rate = _safe_divide(
        sum(1 for result in keyword_cases if set(result.expected_keywords) == set(result.matched_keywords)),
        len(keyword_cases),
    )

    refusal_cases = [result for result in results if result.should_refuse]
    refusal_accuracy = _safe_divide(
        sum(1 for result in refusal_cases if result.refused),
        len(refusal_cases),
    )

    return EvaluationReport(
        total=total,
        passed=passed,
        keyword_hit_rate=keyword_hit_rate,
        refusal_accuracy=refusal_accuracy,
        results=results,
    )


def load_cases(path: str | Path) -> list[EvaluationCase]:
    raw_cases = json.loads(Path(path).read_text(encoding="utf-8"))
    return [
        EvaluationCase(
            question=item["question"],
            documents=item["documents"],
            expected_keywords=item.get("expected_keywords", []),
            should_refuse=item.get("should_refuse", False),
        )
        for item in raw_cases
    ]


def main() -> None:
    parser = argparse.ArgumentParser(description="Evaluate the local RAG pipeline.")
    parser.add_argument("--dataset", default="eval/eval_dataset.json")
    args = parser.parse_args()

    report = evaluate_cases(load_cases(args.dataset))
    print(f"total={report.total}")
    print(f"passed={report.passed}")
    print(f"keyword_hit_rate={report.keyword_hit_rate:.2f}")
    print(f"refusal_accuracy={report.refusal_accuracy:.2f}")
    for result in report.results:
        status = "PASS" if result.passed else "FAIL"
        print(f"- {status} {result.question} -> {result.answer}")


def _evaluate_case(case: EvaluationCase) -> EvaluationResult:
    service = RAGService()
    service.ingest_documents(
        [
            IngestedDocument(
                name=document["name"],
                content=document["content"],
                kind=document.get("kind", "txt"),
            )
            for document in case.documents
        ]
    )
    answer = service.ask(case.question)
    refused = answer.answer == REFUSAL_ANSWER
    matched_keywords = [
        keyword for keyword in case.expected_keywords if keyword in answer.answer
    ]

    if case.should_refuse:
        passed = refused
    else:
        passed = bool(case.expected_keywords) and set(case.expected_keywords) == set(matched_keywords)

    return EvaluationResult(
        question=case.question,
        answer=answer.answer,
        expected_keywords=case.expected_keywords,
        matched_keywords=matched_keywords,
        should_refuse=case.should_refuse,
        refused=refused,
        passed=passed,
    )


def _safe_divide(numerator: int, denominator: int) -> float:
    if denominator == 0:
        return 0.0
    return numerator / denominator


if __name__ == "__main__":
    main()
