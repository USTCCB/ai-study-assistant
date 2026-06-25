"""问答接口"""
from fastapi import APIRouter
from pydantic import BaseModel
from app.services.generator import ask

router = APIRouter()


class AskReq(BaseModel):
    question: str
    top_k: int = 5


@router.post("/ask")
def ask_question(req: AskReq):
    return ask(req.question)
