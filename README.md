# RAG 智能问答

这是一个按多轮迭代建设的 RAG 学习项目。当前处于第 12 轮：新增 `.env` 配置和 OpenAI Responses API LLM 回答生成。

## 当前能力

- 支持读取 `data/raw` 下的 `.txt` 和 `.md` 文件
- 预留 `.pdf` 加载入口，需要安装 `pymupdf`
- 支持固定长度 + overlap 的文本切分
- 支持为 chunk 保留文件名、文档类型、页码、标题等 metadata
- 支持本地 hashing embedding
- 支持内存向量索引和余弦相似度检索
- 支持 Qdrant 向量库适配层
- 支持 BM25 关键词检索
- 支持向量检索 + BM25 的混合召回
- 支持 RRF 融合排序
- 支持轻量 Rerank 精排
- 支持引用来源输出
- 支持低置信上下文拒答
- 支持 FastAPI `/ingest` 和 `/ask` 接口
- 支持 Streamlit 前端演示页面
- 支持本地评估数据集和评估脚本
- 支持安全校验：提示词注入、危险内网 URL
- 支持图式编排：安全检查 -> 混合检索 -> Rerank -> 答案生成
- 支持 OpenAI Responses API 生成自然语言答案
- 未配置 API Key 时自动回退到本地抽取式回答
- 支持返回答案和来源 chunk
- 当没有检索到依据时拒答

## 快速运行

```powershell
python -m pytest
python .\ingest.py --chunk-size 50 --overlap 10
python .\ask.py "系统支持上传什么？"
uvicorn app.main:app --reload
streamlit run web/app.py
python .\eval\evaluate.py --dataset eval/eval_dataset.json
```

## Qdrant 适配

默认仍使用内存向量库，便于本地学习和测试。需要接入 Qdrant 时，先启动 Qdrant 服务并安装依赖：

```powershell
pip install -r requirements.txt
docker run -p 6333:6333 qdrant/qdrant
```

代码中可通过 `RAGService` 传入配置：

```python
service = RAGService(
    embedding_config={"provider": "hashing", "dimensions": 256},
    vector_store_config={
        "provider": "qdrant",
        "url": "http://localhost:6333",
        "collection": "rag_chunks",
        "vector_size": 256,
    },
)
```

## LLM 配置

复制 `.env.example` 为 `.env`，并填入自己的 Key：

```powershell
Copy-Item .env.example .env
```

```text
OPENAI_API_KEY=你的 OpenAI API Key
OPENAI_BASE_URL=https://api.openai.com/v1
OPENAI_MODEL=gpt-4.1-mini
```

`.env` 已加入 `.gitignore`，不要把真实 Key 提交到仓库。未配置 `OPENAI_API_KEY` 时，系统会自动回退到本地抽取式回答。

## 当前评估指标

```text
total=3
passed=3
keyword_hit_rate=1.00
refusal_accuracy=1.00
```

## 迭代方向

后续会逐步加入 Qdrant、FastAPI、Streamlit、RAGAS 和 LangGraph。
