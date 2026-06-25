"""文档上传 + 向量化入库"""
from fastapi import APIRouter, UploadFile, File, HTTPException
from pydantic import BaseModel
from typing import List
import uuid
from app.core.db import SessionLocal
from app.core.models import Document, Chunk
from app.services.splitter import split_text
from app.services.embedder import embed_texts
from sqlalchemy import text

router = APIRouter()


class IngestTextReq(BaseModel):
    title: str
    content: str
    source: str = "manual"


@router.post("/text")
def ingest_text(req: IngestTextReq):
    """文本入库"""
    return _ingest(req.title, req.content, req.source)


@router.post("/file")
async def ingest_file(file: UploadFile = File(...)):
    """文件入库（.txt / .md）"""
    if not file.filename.endswith((".txt", ".md")):
        raise HTTPException(400, "只支持 .txt / .md")
    content = (await file.read()).decode("utf-8", errors="ignore")
    title = file.filename.rsplit(".", 1)[0]
    return _ingest(title, content, source=file.filename)


def _ingest(title: str, content: str, source: str):
    # 1) 切块
    chunks = split_text(content)
    if not chunks:
        raise HTTPException(400, "内容为空")
    # 2) 批 embedding
    vectors = embed_texts(chunks)
    # 3) 写入 DB（pgvector 批量）
    doc_id = uuid.uuid4()
    with SessionLocal() as db:
        db.add(Document(id=doc_id, title=title, source=source))
        # 用 unnest 批量写
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
        db.commit()
    return {"document_id": str(doc_id), "chunks": len(chunks), "title": title}
