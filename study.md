# RAG 智能问答项目学习计划

## 1. 学习目标

本计划参考简历中的两个项目方向：

- 基于 RAG 的产品说明书智能问答系统
- Multi-Agent 智能客服系统

最终目标是在 8 周内完成一个可展示、可写进简历、可用于面试讲解的 RAG 项目：支持 PDF / Markdown / TXT 文档解析、混合检索、重排序、问答生成、引用溯源、安全校验、效果评估，并预留 Agent 化扩展能力。

完成后你应该能清楚讲明：

- RAG 的完整链路：文档解析、切分、向量化、召回、重排、生成、评估
- 为什么要做混合检索：BM25 + 向量检索各自解决什么问题
- 为什么要做 Rerank、RRF、引用溯源和安全校验
- 如何用 RAGAS 或自定义指标评估回答质量
- 如何把普通 RAG 系统升级成带工具调用和流程编排的 Agent 系统

## 2. 建议技术栈

### 基础开发

- Python 3.10+
- FastAPI：后端接口
- Streamlit：快速搭建可交互演示页面
- SQLite：存储文档元数据、问答记录、评估结果
- Docker：后期封装部署环境

### RAG 核心

- LangChain 或 LlamaIndex：理解 RAG 基础链路
- LangGraph：实现可控流程编排，后期扩展 Agent
- Qdrant：向量数据库
- bge-m3：中文 / 多语言向量模型
- BM25：关键词检索，可使用 rank-bm25 或 SQLite FTS5
- Reranker：可选 bge-reranker、jina-reranker 或 API 模型

### 文档处理

- PyMuPDF / pdfplumber：PDF 文本抽取
- MinerU：结构化 PDF 解析，可作为进阶目标
- PaddleOCR 或其他 OCR 工具：图片文字识别，可作为加分项
- Markdown / TXT / CSV / JSON 解析：覆盖常见知识库文件

### 评估与质量保障

- RAGAS：忠实度、相关性、召回质量评估
- pytest：核心模块单元测试
- 自建测试集：10-30 个产品说明书问题

## 3. 项目最终形态

项目名称建议：

> 产品说明书 RAG 智能问答系统

核心功能：

- 上传产品说明书 PDF / Markdown / TXT
- 自动解析文档并切分为知识片段
- 对知识片段建立向量索引和关键词索引
- 用户输入自然语言问题
- 系统执行混合检索：BM25 + 向量检索
- 使用 RRF 融合排序结果
- 使用 Reranker 精排候选片段
- 调用大模型生成答案
- 返回答案、引用来源、命中文档片段
- 对无依据问题拒答或提示信息不足
- 记录问答日志，支持后续评估

进阶功能：

- 图片 OCR 入库
- 表格解析
- URL / 超链接有效性检查
- 安全检测：识别恶意链接、无关问题、提示词注入
- LangGraph 编排检索、校验、生成、反思流程
- 多 Agent 协作：查询改写 Agent、检索 Agent、验证 Agent、回答 Agent

## 4. 8 周学习路线

### 第 1 周：RAG 基础与项目初始化

学习目标：

- 理解 RAG 解决的问题
- 搭建 Python 项目结构
- 跑通最小 RAG Demo

学习内容：

- 大模型幻觉问题与知识库增强生成
- Embedding、Chunk、Retriever、Generator 的概念
- 向量相似度：余弦相似度、TopK
- Prompt 中如何注入检索上下文

实践任务：

- 创建项目目录结构
- 准备 1-2 份产品说明书或技术文档
- 用 PyMuPDF 读取 PDF 文本
- 使用 bge-m3 或其他 embedding 模型生成向量
- 用本地内存或 FAISS / Qdrant 完成一次向量检索
- 调用大模型基于检索结果生成回答

交付物：

- 一个 `ask.py` 命令行脚本
- 输入问题后能返回答案和命中文档片段

面试表达重点：

- RAG 是把外部知识通过检索注入上下文，降低模型幻觉
- 最小链路是：文档加载 -> 切分 -> 向量化 -> 检索 -> 生成

### 第 2 周：文档解析与知识切分

学习目标：

- 让系统能稳定处理不同类型文档
- 理解切分策略对召回质量的影响

学习内容：

- PDF 文本抽取
- Markdown 标题结构解析
- TXT / CSV / JSON 基础解析
- 固定长度切分、按标题切分、递归字符切分
- chunk_size、chunk_overlap 对效果的影响

实践任务：

- 实现统一文档加载接口
- 支持 PDF / Markdown / TXT
- 为每个 chunk 保存 metadata：文件名、页码、标题、段落位置
- 对比 3 种切分方式的召回效果

交付物：

- `document_loader` 模块
- `chunker` 模块
- 一个文档入库脚本 `ingest.py`

面试表达重点：

- 文档解析不只是读取文本，还要保留页码、标题、来源等元数据
- chunk 太大会引入噪声，chunk 太小会丢失语义上下文

### 第 3 周：向量数据库与基础检索

学习目标：

- 掌握 Qdrant 的基本使用
- 完成可持久化的向量知识库

学习内容：

- Qdrant collection、point、payload
- 向量写入、删除、更新、搜索
- metadata 过滤
- TopK 和相似度阈值

实践任务：

- 使用 Qdrant 存储 chunk 向量
- 写入 chunk 文本和 metadata
- 实现根据问题检索相关片段
- 给检索结果增加来源信息

交付物：

- `vector_store` 模块
- 可重复运行的入库和检索流程

面试表达重点：

- 向量数据库负责近似语义检索
- payload 可以保存来源、页码、文档类型等信息，方便引用溯源

### 第 4 周：BM25 + 向量混合检索

学习目标：

- 解决专有名词、型号、参数类问题召回不准的问题
- 实现简历中提到的混合检索能力

学习内容：

- BM25 的基本原理
- 中文分词：jieba
- SQLite FTS5 或 rank-bm25
- 向量检索和关键词检索的优缺点
- RRF 融合排序算法

实践任务：

- 为所有 chunk 建立 BM25 索引
- 同时执行 BM25 检索和向量检索
- 实现 RRF 融合排序
- 对比单路向量检索和混合检索的效果

交付物：

- `keyword_retriever` 模块
- `hybrid_retriever` 模块
- 10 个测试问题的召回对比表

面试表达重点：

- 向量检索适合语义相似问题
- BM25 适合型号、术语、编号、精确关键词问题
- RRF 可以融合不同检索器的排名，降低单一路径失误

### 第 5 周：Rerank、引用溯源与回答生成

学习目标：

- 提升最终答案准确性
- 让回答具备可信来源

学习内容：

- Retriever 和 Reranker 的区别
- Cross-Encoder Rerank 思路
- Prompt 模板设计
- 引用来源格式设计
- 无依据拒答策略

实践任务：

- 对混合检索结果进行 Rerank
- 只把 TopN 高质量片段送入大模型
- 设计回答 Prompt，要求模型仅基于上下文回答
- 输出引用来源：文档名、页码、片段编号
- 当上下文不足时返回“资料中没有找到明确依据”

交付物：

- `reranker` 模块
- `answer_generator` 模块
- 支持引用来源的问答接口

面试表达重点：

- 召回阶段追求覆盖率，Rerank 阶段追求精准度
- 引用溯源能提升系统可信度，也方便人工核查
- 拒答机制比强行回答更适合企业知识库场景

### 第 6 周：FastAPI + Streamlit 完整应用

学习目标：

- 把算法链路变成可演示产品
- 完成一个面试可展示的 Web Demo

学习内容：

- FastAPI 路由、请求体、响应模型
- 文件上传接口
- Streamlit 页面搭建
- 问答历史记录
- 简单异常处理

实践任务：

- 实现文档上传接口
- 实现文档入库接口
- 实现问答接口
- Streamlit 页面支持上传文档、输入问题、查看答案和引用
- 保存问答日志到 SQLite

交付物：

- 后端服务：`app/main.py`
- 前端页面：`web/app.py`
- 可运行 Demo

面试表达重点：

- 项目不只是算法 Demo，还包含完整的文档入库、查询和结果展示链路
- 问答日志可以用于后续评估、优化和问题追踪

### 第 7 周：质量评估、安全校验与测试集

学习目标：

- 建立评估闭环
- 让项目从“能跑”变成“能优化”

学习内容：

- RAGAS 基础指标：Faithfulness、Answer Relevancy、Context Recall
- 自建 Golden Dataset
- 链接有效性检测
- Prompt Injection 风险
- pytest 单元测试

实践任务：

- 人工整理 20 个标准问题和参考答案
- 使用 RAGAS 或自定义脚本评估回答质量
- 统计召回率、准确率、引用命中率
- 增加安全校验：识别无关问题、恶意链接、提示词注入
- 为文档解析、检索融合、拒答逻辑写测试

交付物：

- `eval_dataset.json`
- `evaluate.py`
- `tests/` 测试目录
- 一份评估报告

面试表达重点：

- RAG 系统不能只靠主观感觉，需要测试集和评估指标
- 安全校验可以防止模型把恶意内容带入最终回答
- 评估结果能指导 chunk、TopK、Prompt、Rerank 参数优化

### 第 8 周：LangGraph / Agent 化增强与简历包装

学习目标：

- 对齐简历中的 Agent / LangGraph 能力
- 把项目整理成可展示作品

学习内容：

- LangGraph 节点、边、状态
- 查询改写
- 多步骤检索
- 回答验证
- 工具调用
- Checkpoint 和对话记忆

实践任务：

- 用 LangGraph 重构问答流程
- 设计以下节点：
  - Query Rewrite：改写用户问题
  - Hybrid Retrieve：混合检索
  - Rerank：精排
  - Safety Check：安全校验
  - Generate Answer：生成答案
  - Verify Answer：检查答案是否有依据
- 增加简单对话记忆，支持追问
- 整理 README、架构图和项目截图

交付物：

- `rag_graph` 模块
- 完整 README
- 项目架构图
- 简历项目描述

面试表达重点：

- LangGraph 的价值是让 RAG 流程可控、可观测、可扩展
- 普通 RAG 是一条链路，Agent 化 RAG 可以加入查询改写、工具调用、验证和多轮状态
- Checkpoint 可以保存中间状态，方便恢复、调试和多轮对话

## 5. 推荐项目目录结构

```text
RAG智能问答/
  app/
    main.py
    schemas.py
  rag/
    document_loader.py
    chunker.py
    embeddings.py
    vector_store.py
    keyword_retriever.py
    hybrid_retriever.py
    reranker.py
    answer_generator.py
    rag_graph.py
  web/
    app.py
  data/
    raw/
    processed/
  eval/
    eval_dataset.json
    evaluate.py
  tests/
    test_chunker.py
    test_retriever.py
    test_safety.py
  README.md
  study.md
  requirements.txt
```

## 6. 每周时间安排建议

如果每天可学习 2-3 小时：

- 40% 时间学习概念和看官方文档
- 40% 时间写代码实现
- 20% 时间做实验记录和复盘

建议每天固定输出：

- 今天学了什么
- 遇到什么问题
- 调了哪些参数
- 效果有没有提升
- 明天继续做什么

这类记录后期可以直接转化成 README、面试话术和项目复盘。

## 7. 面试可写项目描述

项目名称：

> 基于 RAG 的产品说明书智能问答系统

项目描述：

> 针对传统产品说明书内容冗长、术语密集、用户检索效率低的问题，设计并实现一套基于 RAG 的智能问答系统。系统支持 PDF / Markdown / TXT 文档解析、知识切分、向量入库、BM25 与向量混合检索、RRF 融合排序、Rerank 精排、引用溯源和无依据拒答，并通过 RAGAS 和自建测试集对回答质量进行评估。

技术栈：

> Python + FastAPI + Streamlit + Qdrant + SQLite + BM25 + bge-m3 + LangGraph + RAGAS

核心工作：

- 设计文档解析与知识切分流程，保留文件名、页码、标题等 metadata，实现答案引用溯源。
- 构建 BM25 关键词检索与 bge-m3 向量检索的混合召回架构，使用 RRF 融合排序提升专有名词和语义问题的召回效果。
- 引入 Reranker 对候选片段精排，只将高相关上下文送入大模型，降低无关上下文干扰。
- 设计无依据拒答、安全校验和链接有效性检查机制，减少幻觉和不安全输出。
- 使用 RAGAS 与自建测试集评估忠实度、相关性和上下文召回率，形成可持续优化闭环。
- 基于 LangGraph 编排查询改写、混合检索、精排、生成和验证节点，为后续 Agent 化客服系统扩展打基础。

量化成果示例：

- 在自建 20-50 条产品问答测试集上，混合检索相比单向量检索提升召回率。
- 引入 Rerank 后，Top3 上下文命中率明显提升。
- 无依据拒答机制减少了模型编造答案的情况。

注意：量化结果必须等你真实测试后再填写，不要提前虚构具体数字。

## 8. 学习优先级

第一优先级：

- 文档解析
- chunk 切分
- embedding
- Qdrant 向量检索
- BM25
- RRF
- Prompt 生成回答

第二优先级：

- Rerank
- 引用溯源
- Streamlit 演示页面
- RAGAS 评估
- pytest 测试

第三优先级：

- MinerU
- OCR
- LangGraph
- Multi-Agent
- Redis 对话记忆
- GraphRAG / Neo4j

建议不要一开始就上 GraphRAG、Neo4j、多 Agent。先把标准 RAG 做扎实，再逐步增加高级能力。

## 9. 常见问题与避坑

### 不要只做一个聊天框

只有聊天框很难体现工程能力。一定要有文档上传、入库、检索、引用、评估等完整链路。

### 不要忽略 metadata

没有 metadata，就很难实现引用溯源，也很难排查错误答案来自哪里。

### 不要盲目调 Prompt

RAG 效果差不一定是 Prompt 问题，更多时候是解析、切分、召回、排序出了问题。

### 不要一开始就追求复杂 Agent

Agent 是加分项，不是基础。基础 RAG 不稳定时，上 Agent 只会让问题更难定位。

### 不要虚构指标

简历里可以写指标，但必须来自真实评估。建议先搭建测试集，再记录每次优化后的数据。

## 10. 最终验收标准

完成本计划后，项目至少应满足：

- 能上传并解析 PDF / Markdown / TXT
- 能完成文档切分和向量入库
- 能同时使用 BM25 和向量检索
- 能融合排序并返回引用来源
- 能基于上下文生成答案
- 能对无依据问题进行拒答
- 有基础 Web 演示页面
- 有 20 条以上测试问题
- 有评估脚本和评估报告
- 有 README 和项目架构说明
- 能在 5 分钟内向面试官讲清楚系统设计和优化点

## 11. 推荐学习顺序总结

```text
Python 工程基础
  -> PDF / 文档解析
  -> 文本切分
  -> Embedding
  -> Qdrant 向量检索
  -> BM25 关键词检索
  -> 混合检索与 RRF
  -> Rerank
  -> Prompt 与答案生成
  -> 引用溯源和拒答
  -> FastAPI / Streamlit
  -> RAGAS 评估
  -> LangGraph 编排
  -> Agent 化增强
```

先做出一个稳定、可解释、可评估的 RAG 系统，再把它包装成具备 Agent 扩展能力的项目，这样最适合学习、面试和简历展示。
