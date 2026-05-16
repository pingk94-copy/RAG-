# RAG 智能问答

这是一个按 8 轮迭代建设的 RAG 学习项目。当前处于第 1 轮：先完成无外部模型依赖的最小 RAG 链路，验证文档加载、切分、检索和回答返回流程。

## 当前能力

- 支持读取 `data/raw` 下的 `.txt` 和 `.md` 文件
- 支持固定长度 + overlap 的文本切分
- 支持基于关键词重叠的轻量检索
- 支持返回答案和来源 chunk
- 当没有检索到依据时拒答

## 快速运行

```powershell
python -m pytest
python .\ask.py "系统支持上传什么？"
```

## 迭代方向

后续会逐步加入 PDF 解析、Embedding、Qdrant、BM25、RRF、Rerank、FastAPI、Streamlit、RAGAS 和 LangGraph。
