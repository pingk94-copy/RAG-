from pathlib import Path


def test_env_is_ignored_and_example_is_present():
    root = Path(__file__).resolve().parents[1]

    gitignore = (root / ".gitignore").read_text(encoding="utf-8")
    example = (root / ".env.example").read_text(encoding="utf-8")

    assert ".env" in gitignore
    assert "OPENAI_API_KEY=" in example
    assert "OPENAI_MODEL=" in example
