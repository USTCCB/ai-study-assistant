import json
import sys
import urllib.request

# 用法：python call_java_chunk.py  (需要先启动 Java 服务)
url = "http://127.0.0.1:9090/api/chunk"
text = open(sys.argv[1], encoding="utf-8").read() if len(sys.argv) > 1 else (
    "Spring Boot 简化了 Spring 应用开发。Java 是一门面向对象的语言。" * 20
)
payload = json.dumps({
    "text": text,
    "chunkSize": 200,
    "overlap": 40,
    "source": sys.argv[2] if len(sys.argv) > 2 else "demo"
}).encode("utf-8")
req = urllib.request.Request(url, data=payload, headers={"Content-Type": "application/json"})
with urllib.request.urlopen(req, timeout=10) as r:
    body = json.loads(r.read().decode("utf-8"))
print(f"chunks={body['data']['total']} took={body['data']['tookMs']}ms")
for c in body["data"]["chunks"][:3]:
    print(f"  [{c['index']}] {c['charCount']}c -> {c['text'][:60]}...")
