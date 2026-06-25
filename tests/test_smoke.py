"""冒烟测试 - 不需要真实 OpenAI Key"""
from app.services.splitter import split_text


def test_split_basic():
    text = "a" * 1200
    chunks = split_text(text)
    assert len(chunks) >= 2
    assert all(len(c) <= 600 for c in chunks)
