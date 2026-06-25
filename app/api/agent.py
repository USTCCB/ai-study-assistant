"""Agent 端点"""
from fastapi import APIRouter
from pydantic import BaseModel
from app.services.agent import run_agent

router = APIRouter()


class AgentQuery(BaseRequest := None) if False else None  # placeholder
from pydantic import BaseModel

class AgentQuery(BaseModel):
    question: str
    max_steps: int = 6


@router.post("/query")
def agent_query(req: AgentQuery):
    return run_agent(req.question, max_steps=req.max_steps)
