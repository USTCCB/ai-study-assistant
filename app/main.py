"""
AI 智能学习助手 - RAG 知识库
"""
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api import documents, qa, agent
from app.core.config import settings


@asynccontextmanager
async def lifespan(app: FastAPI):
    # 启动时初始化 pgvector
    from app.core.db import init_db
    init_db()
    yield


app = FastAPI(
    title="AI Study Assistant",
    description="基于 LangChain + pgvector 的 RAG 知识库问答",
    version="1.0.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(documents.router, prefix="/api/documents", tags=["文档"])
app.include_router(qa.router, prefix="/api/qa", tags=["问答"])
app.include_router(agent.router, prefix="/api/agent", tags="Agent")


@app.get("/")
def root():
    return {"name": "AI Study Assistant", "version": "1.0.0", "docs": "/docs"}


@app.get("/health")
def health():
    return {"status": "ok"}

