from __future__ import annotations

import streamlit as st

from rag.service import RAGService
from web.helpers import build_document_payload


def get_service() -> RAGService:
    if "rag_service" not in st.session_state:
        st.session_state.rag_service = RAGService()
    return st.session_state.rag_service


def main() -> None:
    st.set_page_config(page_title="RAG 智能问答", layout="wide")
    st.title("RAG 智能问答")

    service = get_service()

    with st.sidebar:
        st.header("文档入库")
        document_name = st.text_input("文件名", value="manual.txt")
        document_content = st.text_area(
            "文档内容",
            height=220,
            value="系统支持上传产品说明书、技术文档和常见问题文件。",
        )
        if st.button("入库", type="primary"):
            payload = build_document_payload(document_name, document_content)
            summary = service.ingest_documents([payload])
            st.success(f"已入库 {summary.documents} 个文档，生成 {summary.chunks} 个 chunk")

    question = st.text_input("问题", value="系统支持上传什么？")
    if st.button("提问", type="primary"):
        answer = service.ask(question)
        st.subheader("答案")
        st.write(answer.answer)

        if answer.citations:
            st.subheader("引用")
            for citation in answer.citations:
                st.markdown(f"- `{citation}`")

        if answer.sources:
            st.subheader("来源片段")
            for source in answer.sources:
                heading = f" · {source.heading}" if source.heading else ""
                st.markdown(
                    f"**{source.document_name} p{source.page_number}{heading} #{source.chunk_id}**"
                )
                st.write(source.content)


if __name__ == "__main__":
    main()
