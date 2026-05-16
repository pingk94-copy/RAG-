from pathlib import Path

from rag.document_loader import load_document
from rag.ingest import build_chunks, load_documents


def test_load_txt_document_preserves_basic_metadata(tmp_path: Path):
    path = tmp_path / "manual.txt"
    path.write_text("第一段说明。\n第二段说明。", encoding="utf-8")

    document = load_document(path)

    assert document.name == "manual.txt"
    assert document.kind == "txt"
    assert document.pages[0].page_number == 1
    assert "第一段说明" in document.pages[0].text


def test_load_markdown_tracks_nearest_heading(tmp_path: Path):
    path = tmp_path / "manual.md"
    path.write_text("# 安装说明\n请先接通电源。\n## 蓝牙配置\n打开蓝牙开关。", encoding="utf-8")

    document = load_document(path)

    assert document.kind == "md"
    assert document.pages[0].sections[0].heading == "安装说明"
    assert document.pages[0].sections[1].heading == "蓝牙配置"


def test_build_chunks_adds_metadata_from_document(tmp_path: Path):
    path = tmp_path / "manual.md"
    path.write_text("# 安装说明\n请先接通电源，然后打开设备。", encoding="utf-8")
    document = load_document(path)

    chunks = build_chunks([document], chunk_size=12, overlap=2)

    assert chunks
    assert chunks[0].document_name == "manual.md"
    assert chunks[0].page_number == 1
    assert chunks[0].heading == "安装说明"
    assert chunks[0].chunk_id == 0
    assert "安装说明" in chunks[0].content or "接通电源" in chunks[0].content


def test_load_documents_skips_failed_files_by_default(tmp_path: Path):
    pdf_path = tmp_path / "broken.pdf"
    pdf_path.write_text("not a real pdf", encoding="utf-8")
    txt_path = tmp_path / "manual.txt"
    txt_path.write_text("系统支持上传产品说明书。", encoding="utf-8")

    documents = load_documents(tmp_path)

    assert [document.name for document in documents] == ["manual.txt"]
