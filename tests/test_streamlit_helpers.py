from web.helpers import build_document_payload, format_sources


def test_build_document_payload_uses_filename_and_text():
    payload = build_document_payload(
        name="manual.md",
        content="# 安装\n请接通电源。",
    )

    assert payload.name == "manual.md"
    assert payload.kind == "md"
    assert payload.content == "# 安装\n请接通电源。"


def test_build_document_payload_defaults_to_txt_for_unknown_suffix():
    payload = build_document_payload(name="manual.unknown", content="说明内容")

    assert payload.kind == "txt"


def test_format_sources_includes_page_heading_and_preview():
    sources = [
        {
            "document_name": "manual.txt",
            "page_number": 2,
            "heading": "蓝牙配置",
            "chunk_id": 3,
            "content": "打开蓝牙开关，然后在手机中搜索设备。",
        }
    ]

    formatted = format_sources(sources)

    assert formatted == [
        "manual.txt p2 蓝牙配置 #3：打开蓝牙开关，然后在手机中搜索设备。"
    ]
