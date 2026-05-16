from __future__ import annotations

from dataclasses import dataclass
import os
from pathlib import Path
from typing import Protocol


class LLMClient(Protocol):
    def generate_answer(self, question: str, contexts: list[str]) -> str:
        """Generate an answer from a question and retrieved contexts."""


@dataclass
class OpenAIResponsesLLMClient:
    api_key: str
    base_url: str | None = None
    model: str = "gpt-4.1-mini"
    client: object | None = None

    def __post_init__(self) -> None:
        if self.client is None:
            try:
                from openai import OpenAI  # type: ignore
            except ImportError as exc:
                raise RuntimeError("OpenAI LLM requires optional dependency openai") from exc

            kwargs: dict[str, str] = {"api_key": self.api_key}
            if self.base_url:
                kwargs["base_url"] = self.base_url
            self.client = OpenAI(**kwargs)

    def generate_answer(self, question: str, contexts: list[str]) -> str:
        context_text = "\n\n".join(f"[{index + 1}] {context}" for index, context in enumerate(contexts))
        prompt = (
            "你是一个严谨的 RAG 问答助手。请只依据给定资料回答问题；"
            "如果资料不足，请回答：资料中没有找到明确依据。\n\n"
            f"问题：{question}\n\n资料：\n{context_text}"
        )
        response = self.client.responses.create(model=self.model, input=prompt)
        return response.output_text.strip()


def create_llm_client_from_env(env_path: str | Path = ".env") -> LLMClient | None:
    settings = _load_env_file(Path(env_path))
    api_key = settings.get("OPENAI_API_KEY") or os.getenv("OPENAI_API_KEY")
    if not api_key:
        return None

    base_url = settings.get("OPENAI_BASE_URL") or os.getenv("OPENAI_BASE_URL")
    model = settings.get("OPENAI_MODEL") or os.getenv("OPENAI_MODEL") or "gpt-4.1-mini"
    return OpenAIResponsesLLMClient(api_key=api_key, base_url=base_url, model=model)


def _load_env_file(path: Path) -> dict[str, str]:
    if not path.exists():
        return {}

    settings: dict[str, str] = {}
    for raw_line in path.read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        settings[key.strip()] = value.strip().strip('"').strip("'")
    return settings
