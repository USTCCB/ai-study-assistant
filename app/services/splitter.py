"""文档分块：滑动窗口"""
from typing import List
from app.core.config import settings


def split_text(text: str) -> List[str]:
    """简单 sliding-window：按 chunk_size 切，保留 chunk_overlap 上下文重叠"""
    size = settings.chunk_size
    overlap = settings.chunk_overlap
    chunks = []
    start = 0
    while start < len(text):
        end = min(start + size, len(text))
        chunks.append(text[start:end])
        if end >= len(text):
            break
        start = end - overlap
    return chunks
