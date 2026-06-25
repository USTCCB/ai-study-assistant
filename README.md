# ai-study-assistant

个人学习问答助手 —— 用户上传文档（.txt / .md），系统对文档做切片、
向量化、入 pgvector；用户提问时按余弦相似度取 Top-K，把候选片段
和原问题一起交给 LLM 生成答案，并在每条答案里带"来源 N + 相似度"。

## 技术栈

- Python 3.11
- Web：FastAPI 0.111（接口 + 自动 OpenAPI 文档 `/docs`）
- LLM / Embedding：OpenAI 兼容接口（`openai` SDK 1.x；`OPENAI_BASE_URL`
  可指向 DeepSeek / 其它兼容服务）
- RAG：pgvector（PostgreSQL 16 向量扩展）
- ORM：SQLAlchemy 2.0
- 测试：pytest
- 工程化：Docker / Docker Compose / GitHub Actions

## 目录结构

```
.
+-- app/
|   +-- main.py                FastAPI 入口，挂载 documents / qa / agent 三个 router
|   +-- api/
|   |   +-- documents.py       文档上传/文本入库
|   |   +-- qa.py              问答接口
|   |   +-- agent.py           Function Calling Agent 入口
|   +-- core/
|   |   +-- config.py          pydantic-settings 读 .env
|   |   +-- db.py              SQLAlchemy engine + Session
|   |   +-- models.py          Document / Chunk ORM
|   +-- services/
|       +-- splitter.py        文本切片
|       +-- embedder.py        Embedding 批调用
|       +-- retriever.py       pgvector 余弦相似度 Top-K
|       +-- generator.py       RAG 生成（拼 prompt + 调 LLM）
|       +-- agent.py           Function Calling Agent
+-- tests/
|   +-- test_agent.py          Agent 单测
+-- requirements.txt
+-- Dockerfile
+-- docker-compose.yml         一键起 pgvector + FastAPI
+-- .github/workflows/
    +-- python-ci.yml
```

## 数据流

```
        +--------------------+
        |  上传 .txt / .md   |
        +---------+----------+
                  |
                  v
        +--------------------+        +-------------------+
        |  splitter 切块      |  -->   |  embedder 批向量化 |
        +--------------------+        +---------+---------+
                                                  |
                                                  v
                                        +-------------------+
                                        |  pgvector 批量入库 |
                                        |  unnest(:contents,|
                                        |       :vectors,  |
                                        |       :idxs)      |
                                        +-------------------+
                                                  ^
                                                  |
        +--------------------+        +-----------+-----------+
        |  提问               |  -->   |  retriever Top-K     |
        +--------------------+        |  1 - (emb <=> :qvec) |
                  |                   +-----------+-----------+
                  |                               |
                  v                               v
                +---------------------------------------+
                |  generator：拼 prompt + 调 LLM        |
                |  答案中带 [来源 N] 和相似度            |
                +---------------------------------------+
```

## 本地启动

```bash
docker compose up -d
# FastAPI:  http://localhost:8000  /docs
# pgvector: localhost:5432
```

`.env` 至少需要：

```
OPENAI_API_KEY=sk-...
OPENAI_BASE_URL=https://api.openai.com/v1
LLM_MODEL=gpt-4o-mini
EMBEDDING_MODEL=text-embedding-3-small
DATABASE_URL=postgresql+psycopg2://postgres:postgres@db:5432/ai_study
```

## 主要接口

| Method | Path | 说明 |
|---|---|---|
| POST | /api/documents/text | 文本入库（title + content） |
| POST | /api/documents/file | 文件入库（.txt / .md） |
| POST | /api/qa/ask | 问答，返回 `answer` + 引用片段 |
| POST | /api/agent/run | Function Calling Agent 入口 |

## 关键代码片段

### 1. pgvector 批量入库（`app/api/documents.py`）

```python
sql = text("""
    INSERT INTO chunks (document_id, content, embedding, chunk_index)
    SELECT :doc_id, content, vec, idx
    FROM unnest(:contents::text[], :vectors::vector[], :idxs::int[])
    AS t(content, vec, idx)
""")
db.execute(sql, {
    "doc_id": str(doc_id),
    "contents": chunks,
    "vectors": [str(v) for v in vectors],
    "idxs": list(range(len(chunks))),
})
```

### 2. 余弦相似度 Top-K（`app/services/retriever.py`）

```python
sql = text("""
    SELECT c.content, c.document_id,
           1 - (c.embedding <=> :qvec) AS similarity
    FROM chunks c
    ORDER BY c.embedding <=> :qvec
    LIMIT :k
""")
```

`1 - (embedding <=> :qvec)` 把 pgvector 的 cosine **距离**转成 **相似度**。
返回 `(content, similarity, document_id)`。

### 3. Function Calling Agent

Function Calling Agent 已经抽到独立仓库
[`USTCCB/function-calling-agent`](https://github.com/USTCCB/function-calling-agent)，
便于单独 review 工具分发 / 主循环 / 异常兜底。本仓库保留 `app/services/agent.py`
作为入口，挂载在 `/api/agent/run`。

## 测试

```bash
pytest -q
```

CI 在 push / PR 时自动跑（见 `.github/workflows/python-ci.yml`）。
