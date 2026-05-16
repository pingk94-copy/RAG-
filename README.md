# RAG 智能问答

这是一个按 8 轮迭代建设的 RAG 学习项目。当前处于第 5 轮：在混合检索后加入 Rerank 精排、引用来源和低置信拒答。

## 当前能力

- 支持读取 `data/raw` 下的 `.txt` 和 `.md` 文件
- 预留 `.pdf` 加载入口，需要安装 `pymupdf`
- 支持固定长度 + overlap 的文本切分
- 支持为 chunk 保留文件名、文档类型、页码、标题等 metadata
- 支持本地 hashing embedding
- 支持内存向量索引和余弦相似度检索
- 支持 BM25 关键词检索
- 支持向量检索 + BM25 的混合召回
- 支持 RRF 融合排序
- 支持轻量 Rerank 精排
- 支持引用来源输出
- 支持低置信上下文拒答
- 支持返回答案和来源 chunk
- 当没有检索到依据时拒答

## 快速运行

```powershell
python -m pytest
python .\ingest.py --chunk-size 50 --overlap 10
python .\ask.py "系统支持上传什么？"
```

## 迭代方向

后续会逐步加入 Qdrant、FastAPI、Streamlit、RAGAS 和 LangGraph。
