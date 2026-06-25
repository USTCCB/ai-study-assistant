"""把 data/sample.md 入库"""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import requests

BASE = "http://localhost:8000"
with open(os.path.join(os.path.dirname(__file__), "..", "data", "sample.md"), "r", encoding="utf-8") as f:
    content = f.read()

r = requests.post(f"{BASE}/api/documents/text", json={
    "title": "Java 并发笔记",
    "content": content,
    "source": "sample.md"
})
print(r.status_code, r.json())
