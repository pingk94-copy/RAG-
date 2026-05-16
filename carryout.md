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

## 第 5 轮：Rerank 精排、引用来源与拒答

完成时间：2026-05-16

本轮目标：

- 在混合召回后增加精排层
- 统一答案生成出口
- 输出可读引用来源
- 增加低置信上下文拒答

完成内容：

- 新增 `rag/reranker.py`，实现 `SimpleReranker`
- 新增 `rag/answer_generator.py`，实现 `AnswerGenerator`
- `SimpleReranker` 基于问题与候选片段 token overlap 进行二次排序
- `AnswerGenerator` 支持按最低分阈值拒答
- `AnswerGenerator` 支持输出 citation：文档名、页码、标题、chunk id
- 更新 `ask.py`，完整链路变为 `Hybrid Retrieve -> Rerank -> Generate Answer`
- 新增 `tests/test_answer_generation.py`，覆盖精排、引用和低置信拒答

验证结果：

- `python -m pytest`：16 个测试通过
- `python .\ask.py "系统支持上传什么？"`：成功返回答案、引用和 rerank 分数
- `python .\ask.py "今天西安天气怎么样？"`：成功拒答

下一轮计划：

- 搭建 FastAPI 服务
- 提供 `/ingest` 和 `/ask` 接口
- 为后续 Streamlit 前端准备稳定 API

## 第 6 轮：FastAPI 服务接口

完成时间：2026-05-16

本轮目标：

- 将现有 RAG 链路封装成可复用服务对象
- 搭建 FastAPI 应用
- 提供文档入库和问答接口
- 为下一轮 Streamlit 前端准备稳定 API

完成内容：

- 新增 `rag/service.py`，实现 `RAGService`
- `RAGService` 统一封装 ingest、混合检索、rerank、answer generation
- 新增 `app/main.py`，提供 FastAPI 应用
- 新增 `/health` 健康检查接口
- 新增 `/ingest` 接口，支持通过 JSON 提交文档内容
- 新增 `/ask` 接口，返回答案、引用和来源片段
- 更新 `ask.py`，复用 `RAGService`，避免命令行和 API 维护两套链路
- 新增 `tests/test_api.py`，覆盖 API 入库、问答和无依据拒答

验证结果：

- `python -m pytest`：18 个测试通过
- `python .\ask.py "系统支持上传什么？"`：成功返回答案、引用和来源

下一轮计划：

- 搭建 Streamlit 前端页面
- 支持页面上传 / 输入文档内容
- 支持页面提问、展示答案、引用和来源片段

## 第 7 轮：Streamlit 前端演示页面

完成时间：2026-05-16

本轮目标：

- 搭建可视化前端页面
- 支持在页面中输入文档并入库
- 支持在页面中提问
- 展示答案、引用和来源片段

完成内容：

- 新增 `web/app.py`，实现 Streamlit 页面
- 新增 `web/helpers.py`，封装前端文档 payload 构建和来源格式化
- 页面侧边栏支持输入文件名和文档内容并执行入库
- 页面主区域支持输入问题并展示答案
- 页面支持展示 citation 和来源 chunk
- 新增 `tests/test_streamlit_helpers.py`，覆盖前端辅助逻辑
- 更新 `requirements.txt`，加入 `streamlit`
- 更新 README，加入 `streamlit run web/app.py` 启动命令

验证结果：

- `python -m pytest`：21 个测试通过
- 本地当前未安装 Streamlit，未启动页面；安装依赖后可运行 `streamlit run web/app.py`

下一轮计划：

- 增加评估数据集和评估脚本
- 统计回答是否命中参考答案关键词
- 输出简单评估报告，为 RAGAS 接入打基础

## 第 8 轮：评估数据集与质量闭环

完成时间：2026-05-16

本轮目标：

- 增加本地评估数据集
- 增加自动评估脚本
- 统计关键词命中和拒答准确率
- 为后续接入 RAGAS 打基础

完成内容：

- 新增 `eval/eval_dataset.json`，包含 3 条基础评估样例
- 新增 `eval/evaluate.py`，支持读取数据集并运行 RAGService
- 定义 `EvaluationCase`、`EvaluationResult`、`EvaluationReport`
- 评估脚本输出 total、passed、keyword_hit_rate、refusal_accuracy
- 新增 `tests/test_evaluation.py`，覆盖关键词命中和拒答评估
- 更新 README，加入评估脚本运行命令和当前指标

验证结果：

- `python -m pytest`：22 个测试通过
- `python .\eval\evaluate.py --dataset eval/eval_dataset.json`：
  - `total=3`
  - `passed=3`
  - `keyword_hit_rate=1.00`
  - `refusal_accuracy=1.00`

下一轮计划：

- 如果继续迭代，建议进入项目增强阶段：
  - 增加 LangGraph 编排
  - 增加安全校验
  - 接入真实 embedding / Qdrant
  - 扩展评估集并接入 RAGAS

## 第 9 轮：Embedding 工厂与 Qdrant 适配层

完成时间：2026-05-16

本轮目标：

- 增加可配置 embedding 创建入口
- 增加 Qdrant 向量库适配层
- 保持默认内存向量库可测试、可运行
- 为后续真实 embedding / Qdrant 服务接入打好边界

完成内容：

- 更新 `rag/embeddings.py`，新增 `create_embedding_model`
- 新增 `rag/qdrant_store.py`，实现 `QdrantVectorStore`
- `QdrantVectorStore` 支持 collection 配置、向量写入、向量搜索和清空
- 更新 `rag/service.py`，支持 `embedding_config` 和 `vector_store_config`
- 默认配置仍为 hashing embedding + memory vector store
- 新增 `tests/test_vector_backend.py`，覆盖 embedding 工厂、Qdrant 依赖提示和服务配置
- 更新 README，加入 Qdrant 启动和配置示例
- 更新 `requirements.txt`，加入 `qdrant-client`

验证结果：

- `python -m pytest`：26 个测试通过

下一轮计划：

- 增加安全校验模块
- 识别无关问题、提示词注入和危险链接
- 在答案生成前加入安全拒答
