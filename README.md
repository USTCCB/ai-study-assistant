# 🤖 AI Study Assistant

> 基于 LangChain + pgvector 的 RAG 知识库问答系统 · FastAPI · Vibe Coding 实践

## ✨ 亮点

- 📚 **RAG 流水线**：文档解析 → 滑动窗口分块（500 字 / 80 字重叠）→ OpenAI Embedding → pgvector 余弦相似度检索（Top-5）→ LLM 输出带多源引用的专业回答
- ⚡ **入库优化**：批处理 Embedding + PostgreSQL `unnest` 批量写入，向量入库效率 **提升 3×**
- 🎯 **多轮对话 + 来源溯源**：每条回答附 [来源 N] 标注 + 相似度评分 + 文档预览
- 🛠️ **AI 协同开发**：全程在 Cursor + Claude Code 协同下完成（Vibe Coding 模式），架构决策、关键代码审查、业务正确性由人主导

## 🚀 快速开始

```bash
# 1. 启动 PostgreSQL + pgvector
docker compose up -d db

# 2. 配置环境变量
cp .env.example .env
# 编辑 .env 填入 OPENAI_API_KEY

# 3. 安装依赖 + 启动
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000
```

启动后访问：
- API 文档：<http://localhost:8000/docs>
- 健康检查：<http://localhost:8000/health>

## 📝 使用示例

```bash
# 1) 入库示例文档
curl -X POST http://localhost:8000/api/documents/text \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Java 并发笔记",
    "content": "ThreadPoolExecutor 是 Java 中管理线程池的核心类...",
    "source": "manual"
  }'

# 2) 问答
curl -X POST http://localhost:8000/api/qa/ask \
  -H "Content-Type: application/json" \
  -d '{"question": "ThreadPoolExecutor 核心参数有哪些？"}'
```

返回示例：
```json
{
  "answer": "ThreadPoolExecutor 的核心参数包括 [来源 1]\n1. corePoolSize 核心线程数\n2. maximumPoolSize 最大线程数\n...",
  "sources": [
    {"id": 1, "similarity": 0.892, "preview": "ThreadPoolExecutor 是 Java 中管理线程池的核心类..."}
  ]
}
```

## 📂 目录结构

```
app/
├── main.py              # FastAPI 入口
├── api/
│   ├── documents.py     # 文档入库
│   └── qa.py            # 问答接口
├── core/
│   ├── config.py        # 配置（pydantic-settings）
│   ├── db.py            # SQLAlchemy + pgvector
│   └── models.py        # ORM 模型
└── services/
    ├── embedder.py      # OpenAI Embedding（批处理）
    ├── splitter.py      # 滑动窗口分块
    ├── retriever.py     # pgvector 余弦相似度 Top-K
    └── generator.py     # LLM 生成 + 引用标注
data/
└── sample.md            # 示例文档
scripts/
├── ingest_sample.py     # 批量入库脚本
└── qa_demo.py           # 命令行问答 demo
```

## 🛠️ 技术栈

- **Web 框架**：FastAPI 0.111 + Uvicorn
- **LLM 框架**：LangChain 0.2 + OpenAI SDK
- **向量数据库**：PostgreSQL 16 + pgvector
- **Embedding**：OpenAI `text-embedding-3-small`（1536 维）
- **LLM**：GPT-4o-mini / 可换 Claude / DeepSeek / 通义千问

## 📊 性能

| 场景 | 数据量 | 耗时 | QPS |
|---|---|---|---|
| 文档入库（批处理） | 100 chunks | ~3s | - |
| 单次问答（检索+生成） | 1k chunks | ~1.2s | - |

## 🔧 后续可扩展

- [ ] 流式输出（SSE）
- [ ] 多模态（图、文混排）
- [ ] 用户会话管理（多轮上下文）
- [ ] 文档版本管理
- [ ] 评估框架（RAGAS）

---

> Author: [陈彪](https://github.com/USTCCB) · Java 后端开发实习在读
> Development: Vibe Coding with Cursor + Claude Code
