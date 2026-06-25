"""向量检索：pgvector 余弦相似度 Top-K"""
from typing import List, Tuple
from sqlalchemy import text
from app.core.db import SessionLocal
from app.services.embedder import embed_query
from app.core.config import settings


def retrieve(query: str, top_k: int = None) -> List[Tuple[str, float, str]]:
    """返回 [(content, similarity, source), ...]"""
    k = top_k or settings.top_k
    qvec = embed_query(query)
    # pgvector cosine distance → 取最近的 k 个
    sql = text("""
        SELECT c.content, c.document_id, 1 - (c.embedding <=> :qvec) AS similarity
        FROM chunks c
        ORDER BY c.embedding <=> :qvec
        LIMIT :k
    """)
    with SessionLocal() as db:
        rows = db.execute(sql, {"qvec": qvec, "k": k}).fetchall()
    # 取 source
    out = []
    for r in rows:
        sim = float(r.similarity)
        out.append((r.content, sim, str(r.document_id)))
    return out
