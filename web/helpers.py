from __future__ import annotations

from rag.service import IngestedDocument


def build_document_payload(name: str, content: str) -> IngestedDocument:
    suffix = name.rsplit(".", 1)[-1].lower() if "." in name else "txt"
    kind = suffix if suffix in {"txt", "md", "pdf"} else "txt"
    return IngestedDocument(name=name, content=content, kind=kind)


def format_sources(sources: list[dict[str, object]]) -> list[str]:
    formatted: list[str] = []
    for source in sources:
        heading = f" {source['heading']}" if source.get("heading") else ""
        content = str(source.get("content", "")).replace("\n", " ")
        formatted.append(
            f"{source['document_name']} p{source['page_number']}"
            f"{heading} #{source['chunk_id']}：{content}"
        )
    return formatted
