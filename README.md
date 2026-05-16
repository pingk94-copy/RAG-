# RAG 智能问答

这是一个按 8 轮迭代建设的 RAG 学习项目。当前处于第 2 轮：在最小 RAG 链路基础上，补齐统一文档加载、Markdown 标题识别和 chunk metadata。

## 当前能力

- 支持读取 `data/raw` 下的 `.txt` 和 `.md` 文件
- 预留 `.pdf` 加载入口，需要安装 `pymupdf`
- 支持固定长度 + overlap 的文本切分
- 支持为 chunk 保留文件名、文档类型、页码、标题等 metadata
- 支持基于关键词重叠的轻量检索
- 支持返回答案和来源 chunk
- 当没有检索到依据时拒答

## 快速运行

```powershell
python -m pytest
python .\ingest.py --chunk-size 50 --overlap 10
python .\ask.py "系统支持上传什么？"
```

## 迭代方向

后续会逐步加入 PDF 解析、Embedding、Qdrant、BM25、RRF、Rerank、FastAPI、Streamlit、RAGAS 和 LangGraph。
