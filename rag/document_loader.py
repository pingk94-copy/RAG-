from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import re


@dataclass(frozen=True)
class DocumentSection:
    heading: str | None
    text: str


@dataclass(frozen=True)
class DocumentPage:
    page_number: int
    text: str
    sections: list[DocumentSection]


@dataclass(frozen=True)
class LoadedDocument:
    name: str
    kind: str
    path: str
    pages: list[DocumentPage]


def load_document(path: str | Path) -> LoadedDocument:
    file_path = Path(path)
    suffix = file_path.suffix.lower()
    if suffix == ".txt":
        return _load_plain_text(file_path, "txt")
    if suffix == ".md":
        return _load_markdown(file_path)
    if suffix == ".pdf":
        return _load_pdf_placeholder(file_path)
    raise ValueError(f"Unsupported document type: {suffix}")


def _load_plain_text(path: Path, kind: str) -> LoadedDocument:
    text = path.read_text(encoding="utf-8")
    page = DocumentPage(
        page_number=1,
        text=text,
        sections=[DocumentSection(heading=None, text=text)],
    )
    return LoadedDocument(name=path.name, kind=kind, path=str(path), pages=[page])


def _load_markdown(path: Path) -> LoadedDocument:
    text = path.read_text(encoding="utf-8")
    sections = _split_markdown_sections(text)
    page = DocumentPage(page_number=1, text=text, sections=sections)
    return LoadedDocument(name=path.name, kind="md", path=str(path), pages=[page])


def _split_markdown_sections(text: str) -> list[DocumentSection]:
    sections: list[DocumentSection] = []
    current_heading: str | None = None
    current_lines: list[str] = []

    for line in text.splitlines():
        match = re.match(r"^\s{0,3}(#{1,6})\s+(.+?)\s*$", line)
        if match:
            if current_heading is not None or current_lines:
                sections.append(
                    DocumentSection(
                        heading=current_heading,
                        text="\n".join(current_lines).strip(),
                    )
                )
            current_heading = match.group(2).strip()
            current_lines = [current_heading]
            continue
        current_lines.append(line)

    if current_heading is not None or current_lines:
        sections.append(
            DocumentSection(
                heading=current_heading,
                text="\n".join(current_lines).strip(),
            )
        )

    return sections or [DocumentSection(heading=None, text=text)]


def _load_pdf_placeholder(path: Path) -> LoadedDocument:
    try:
        import fitz  # type: ignore
    except ImportError as exc:
        raise RuntimeError("PDF support requires PyMuPDF. Install it with: pip install pymupdf") from exc

    pages: list[DocumentPage] = []
    with fitz.open(path) as pdf:
        for index, page in enumerate(pdf, start=1):
            text = page.get_text()
            pages.append(
                DocumentPage(
                    page_number=index,
                    text=text,
                    sections=[DocumentSection(heading=None, text=text)],
                )
            )

    return LoadedDocument(name=path.name, kind="pdf", path=str(path), pages=pages)
