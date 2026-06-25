"""问答 demo"""
import requests

q = input("问：")
r = requests.post("http://localhost:8000/api/qa/ask", json={"question": q})
data = r.json()
print("\n=== 回答 ===")
print(data["answer"])
print("\n=== 引用 ===")
for s in data.get("sources", []):
    print(f"[{s['id']}] 相似度={s['similarity']} 预览={s['preview']}")
