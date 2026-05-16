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
