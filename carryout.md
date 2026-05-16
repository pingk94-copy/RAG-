# 迭代执行记录

## 第 1 轮：最小 RAG Demo

完成时间：2026-05-16

本轮目标：

- 搭建项目基础目录
- 跑通“文档 -> 切分 -> 检索 -> 回答”的最小链路
- 用测试固定核心行为

完成内容：

- 新增 `rag/chunker.py`，实现带 overlap 的文本切分
- 新增 `rag/simple_rag.py`，实现轻量级本地 RAG 流程
- 新增 `ask.py`，支持命令行基于本地文档提问
- 新增 `data/raw/sample_manual.txt`，作为第一份样例文档
- 新增 `tests/test_core.py`，覆盖切分、命中回答、无依据拒答
- 新增 `README.md` 和 `requirements.txt`

验证结果：

- `python -m pytest tests/test_core.py`：3 个测试通过

下一轮计划：

- 增加 PDF / Markdown / TXT 的统一文档加载模块
- 为 chunk 增加 metadata：文件名、页码、标题、段落位置
- 形成可复用的 `ingest.py` 入库脚本

## 第 2 轮：文档加载与 Chunk Metadata

完成时间：2026-05-16

本轮目标：

- 增加统一文档加载模块
- 支持 TXT / Markdown / PDF 入口
- 为 chunk 记录可追溯 metadata
- 提供入库预览脚本

完成内容：

- 新增 `rag/document_loader.py`，定义 `LoadedDocument`、`DocumentPage`、`DocumentSection`
- 支持 `.txt` 文档读取并生成默认页码
- 支持 `.md` 文档读取，并按 Markdown 标题拆分 section
- 预留 `.pdf` 读取入口，使用 PyMuPDF 逐页抽取文本
- 新增 `rag/ingest.py`，将文档转换为带 metadata 的 `KnowledgeChunk`
- 新增 `ingest.py` 命令行脚本，用于预览文档解析和 chunk 结果
- 更新 `ask.py`，复用统一加载和 chunk 构建流程
- 新增 `tests/test_document_loader.py`，覆盖 TXT、Markdown 和 chunk metadata

验证结果：

- `python -m pytest`：6 个测试通过
- `python .\ingest.py --chunk-size 50 --overlap 10`：成功解析 1 个文档并生成 2 个 chunk
- `python .\ask.py "系统支持上传什么？"`：成功返回答案和来源 chunk

下一轮计划：

- 引入向量表示和持久化检索层
- 设计可替换的 embedding 接口
- 初步接入 Qdrant 或先实现本地向量索引适配层

## 第 3 轮：Embedding 接口与本地向量检索

完成时间：2026-05-16

本轮目标：

- 引入向量表示能力
- 设计可替换的 embedding 接口
- 实现本地向量索引适配层
- 将命令行问答切换到向量检索链路

完成内容：

- 新增 `rag/embeddings.py`，定义 `EmbeddingModel` 协议和 `HashingEmbeddingModel`
- `HashingEmbeddingModel` 使用稳定 hash 生成本地向量，方便无 API Key 环境运行
- 新增 `rag/vector_store.py`，实现 `InMemoryVectorStore` 和余弦相似度检索
- 新增 `rag/vector_rag.py`，封装基于向量检索的问答流程
- 更新 `ask.py`，从关键词重叠检索切换为本地向量检索
- 新增 `tests/test_vector_store.py`，覆盖 embedding 稳定性、向量检索、清空索引和向量问答

验证结果：

- `python -m pytest`：10 个测试通过
- `python .\ingest.py --chunk-size 50 --overlap 10`：成功解析样例文档并生成 chunk
- `python .\ask.py "系统支持上传什么？"`：成功通过向量检索返回答案和来源

下一轮计划：

- 引入 BM25 关键词检索
- 实现向量检索 + BM25 的混合召回
- 使用 RRF 融合两路检索结果

## 第 4 轮：BM25 混合检索与 RRF 融合

完成时间：2026-05-16

本轮目标：

- 增加 BM25 关键词检索能力
- 将关键词检索与向量检索进行混合召回
- 使用 RRF 融合两路检索排名
- 将命令行问答切换到混合检索链路

完成内容：

- 新增 `rag/keyword_retriever.py`，实现轻量 BM25 检索器
- 新增 `rag/hybrid_retriever.py`，实现 `HybridRetriever`
- 新增 `reciprocal_rank_fusion`，融合向量检索和 BM25 检索排名
- 更新 `ask.py`，实际问答流程改为 `vector + keyword -> RRF -> answer`
- 新增 `tests/test_hybrid_retriever.py`，覆盖 BM25 精确型号命中、RRF 融合和混合检索

验证结果：

- `python -m pytest`：13 个测试通过
- `python .\ask.py "系统支持上传什么？"`：成功返回答案，来源显示 `via=keyword,vector`

下一轮计划：

- 增加 Rerank 精排层
- 设计统一 AnswerGenerator
- 优化引用来源展示和无依据拒答阈值
