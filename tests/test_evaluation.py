from eval.evaluate import EvaluationCase, evaluate_cases


def test_evaluate_cases_scores_keyword_hits_and_refusals():
    cases = [
        EvaluationCase(
            question="系统支持上传什么？",
            documents=[
                {
                    "name": "manual.txt",
                    "content": "系统支持上传产品说明书和技术文档。",
                    "kind": "txt",
                }
            ],
            expected_keywords=["产品说明书", "技术文档"],
            should_refuse=False,
        ),
        EvaluationCase(
            question="今天西安天气怎么样？",
            documents=[
                {
                    "name": "manual.txt",
                    "content": "系统支持上传产品说明书。",
                    "kind": "txt",
                }
            ],
            expected_keywords=[],
            should_refuse=True,
        ),
    ]

    report = evaluate_cases(cases)

    assert report.total == 2
    assert report.keyword_hit_rate == 1.0
    assert report.refusal_accuracy == 1.0
    assert report.results[0].passed is True
    assert report.results[1].passed is True
