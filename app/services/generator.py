"""LLM 生成带引用的回答"""
from openai import OpenAI
from app.core.config import settings
from app.services.retriever import retrieve

_client = OpenAI(api_key=settings.openai_api_key, base_url=settings.openai_base_url)


SYSTEM_PROMPT = """你是 AI 学习助手。基于下面提供的【参考资料】回答用户问题，要求：
1. 回答必须基于参考资料，事实清晰
2. 在引用处标注 [来源 N]
3. 如果参考资料无法回答，明确告知并建议用户上传更多资料
4. 用中文回答，技术问题给出代码示例

【参考资料】
{context}
"""


def ask(question: str) -> dict:
    docs = retrieve(question)
    if not docs:
        return {"answer": "抱歉，没有找到相关资料。", "sources": []}

    context_parts = []
    sources = []
    for i, (content, sim, source) in enumerate(docs, 1):
        context_parts.append(f"[来源 {i}] (相似度 {sim:.2f})\n{content}\n")
        sources.append({"id": i, "similarity": round(sim, 3), "document_id": source, "preview": content[:200]})

    context = "\n\n".join(context_parts)
    prompt = SYSTEM_PROMPT.format(context=context)

    resp = _client.chat.completions.create(
        model=settings.llm_model,
        messages=[
            {"role": "system", "content": prompt},
            {"role": "user", "content": question},
        ],
        temperature=0.3,
    )
    answer = resp.choices[0].message.content
    return {"answer": answer, "sources": sources}
