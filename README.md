# ai-study-assistant

个人学习问答助手 —— **前端 FastAPI + Python，文档切片/批处理用 Java**。

- Python：FastAPI 0.111 + LangChain + pgvector + OpenAI/Claude API
- Java 工具：Spring Boot 3.2 + Java 17（java-tools/），负责文档滑动窗口切片、对内提供 /api/chunk HTTP 服务
- 数据：PostgreSQL + pgvector
- 工具：Docker / Docker Compose / GitHub Actions

## 目录结构

`
.
├── app/                Python FastAPI 主服务（接口、检索、生成、Embedding）
├── scripts/            离线脚本（ingest、QA demo）
├── data/               示例文档
├── tests/              Python 单测
├── java-tools/         Java 子项目：离线文档切片 HTTP 服务
│   ├── pom.xml
│   ├── Dockerfile
│   ├── examples/call_java_chunk.py  Python 调用 Java 的样例
│   └── src/main/java/com/ustccb/aistudy
│       ├── AiStudyJavaToolsApplication.java
│       ├── controller/ChunkController.java
│       ├── service/ChunkService.java
│       ├── dto/ChunkRequest/ChunkResponse/Chunk/ApiResponse
│       └── src/test/...   JUnit5 单元测试
└── .github/workflows/
    ├── python-ci.yml
    └── java-tools-ci.yml
`

## Java 工具：为什么 + 怎么用

Python 端做切片太慢，Java 用 String.substring 切大文本更快，且**和主项目解耦**（独立 java-tools/ Spring Boot 子项目）。

`ash
cd java-tools
mvn spring-boot:run            # 启动 :9090

# 另一个终端：Python 调 Java
python examples/call_java_chunk.py ../data/sample.md
`

接口：

| Method | Path           | 说明 |
|--------|----------------|------|
| POST   | /api/chunk     | 文本 → chunk 列表（滑动窗口，句子边界优先） |
| GET    | /api/health    | 健康检查 |
| GET    | /actuator/health | actuator |

请求体：

`json
{ "text": "一大段文本...", "chunkSize": 500, "overlap": 80, "source": "data/sample.md" }
`

## 本地启动

`ash
docker compose up -d
# Python: http://localhost:8000  /docs
# Java  : http://localhost:9090  /actuator/health
`

## CI

- python-ci.yml：Python 单测
- java-tools-ci.yml：Java 端 mvn clean verify + 上传 jar
