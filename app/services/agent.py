"""
LLM Function Calling Agent
- 定义一组工具（Tools）
- LLM 自己决定调哪个、调几次
- Agent 主循环：直到 LLM 不再要求调工具才返回最终答案
- 支持多轮"思考 → 调工具 → 观察 → 再思考"
"""
from __future__ import annotations
import json
import logging
from typing import Callable

from openai import OpenAI

from app.core.config import settings
from app.services.retriever import retrieve

log = logging.getLogger(__name__)

_client = OpenAI(api_key=settings.openai_api_key, base_url=settings.openai_base_url)


# ========== 工具定义（OpenAI Function Calling 格式） ==========

TOOLS_SCHEMA = [
    {
        "type": "function",
        "function": {
            "name": "search_knowledge_base",
            "description": "在用户上传的私有知识库里检索相关内容，返回最相似的 top_k 个文档片段。",
            "parameters": {
                "type": "object",
                "properties": {
                    "query": {"type": "string", "description": "检索关键词（中文）"},
                    "top_k": {"type": "integer", "description": "返回前 k 个", "default": 5},
                },
                "required": ["query"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "calculator",
            "description": "对两个数字做四则运算（加 / 减 / 乘 / 除）。",
            "parameters": {
                "type": "object",
                "properties": {
                    "a": {"type": "number"},
                    "b": {"type": "number"},
                    "op": {"type": "string", "enum": ["add", "sub", "mul", "div"]},
                },
                "required": ["a", "b", "op"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "get_current_time",
            "description": "返回服务器当前时间。",
            "parameters": {"type": "object", "properties": {}, "required": []},
        },
    },
]


# ========== 工具实现（本地 Python 函数） ==========

def _search_kb(query: str, top_k: int = 5) -> str:
    """真实工具：调 RAG 检索"""
    try:
        hits = retrieve(query, top_k=top_k)
        if not hits:
            return "（未检索到相关内容）"
        # 简化输出：id + 摘要
        return "\n".join(
            f"[来源 {i+1}] {h.get('content', '')[:200]}" for i, h in enumerate(hits)
        )
    except Exception as e:
        log.exception("search_knowledge_base failed")
        return f"（检索失败：{e}）"


def _calculator(a: float, b: float, op: str) -> str:
    if op == "add": return str(a + b)
    if op == "sub": return str(a - b)
    if op == "mul": return str(a * b)
    if op == "div": return "NaN" if b == 0 else str(a / b)
    return f"unknown op: {op}"


def _get_current_time() -> str:
    from datetime import datetime
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")


TOOL_DISPATCH: dict[str, Callable[..., str]] = {
    "search_knowledge_base": lambda **kw: _search_kb(**kw),
    "calculator":            lambda **kw: _calculator(**kw),
    "get_current_time":      lambda **kw: _get_current_time(),
}


# ========== Agent 主循环 ==========

SYSTEM = """你是 AI 学习助手 Agent。当用户问题需要查资料或做计算时，主动调用合适的工具。
- 需要私有知识时调 search_knowledge_base
- 需要算术时调 calculator
- 需要时间信息时调 get_current_time
- 没有合适的工具就直接回答。最终回答用中文。"""


def run_agent(question: str, max_steps: int = 6) -> dict:
    """ReAct 风格 Agent 循环：直到 LLM 不再要求调工具"""
    messages = [
        {"role": "system", "content": SYSTEM},
        {"role": "user", "content": question},
    ]
    steps: list[dict] = []

    for step in range(max_steps):
        resp = _client.chat.completions.create(
            model=settings.llm_model,
            messages=messages,
            tools=TOOLS_SCHEMA,
            tool_choice="auto",
            temperature=0.2,
        )
        msg = resp.choices[0].message
        # LLM 可能直接给出最终答案（finish_reason=stop），也可能要求调工具
        if not msg.tool_calls:
            return {
                "answer": msg.content or "",
                "steps": steps,
                "total_steps": step,
                "finish_reason": "stop",
            }
        # 把 LLM 的"调工具决定"加入 messages
        messages.append({
            "role": "assistant",
            "content": msg.content,
            "tool_calls": [
                {
                    "id": tc.id,
                    "type": "function",
                    "function": {"name": tc.function.name, "arguments": tc.function.arguments},
                }
                for tc in msg.tool_calls
            ],
        })
        # 执行每个工具调用
        for tc in msg.tool_calls:
            name = tc.function.name
            try:
                args = json.loads(tc.function.arguments or "{}")
            except json.JSONDecodeError:
                args = {}
            fn = TOOL_DISPATCH.get(name)
            if fn is None:
                result = f"unknown tool: {name}"
            else:
                try:
                    result = fn(**args)
                except Exception as e:
                    result = f"tool error: {e}"
            messages.append({"role": "tool", "tool_call_id": tc.id, "content": result})
            steps.append({"step": step, "tool": name, "args": args, "result_preview": str(result)[:120]})

    # 达到 max_steps 还没收敛
    return {
        "answer": "（Agent 达到最大步数未给出最终答案）",
        "steps": steps,
        "total_steps": max_steps,
        "finish_reason": "max_steps",
    }
