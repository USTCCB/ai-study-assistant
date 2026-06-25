"""Embedding 封装 + 批处理优化"""
from typing import List
from openai import OpenAI
from app.core.config import settings

_client = OpenAI(api_key=settings.openai_api_key, base_url=settings.openai_base_url)


def embed_texts(texts: List[str]) -> List[List[float]]:
    """批量 embedding（节省 3× 调用次数）"""
    if not texts:
        return []
    resp = _client.embeddings.create(model=settings.embedding_model, input=texts)
    return [d.embedding for d in resp.data]


def embed_query(q: str) -> List[float]:
    return embed_texts([q])[0]
