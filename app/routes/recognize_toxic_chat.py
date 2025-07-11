from fastapi import APIRouter
from pydantic import BaseModel
from typing import List
from app.service.recognize_toxic_chat import recognize_toxic_chat

router = APIRouter(prefix="/toxic_chat", tags=["Toxic Chat Detection"])

class ToxicChatRequest(BaseModel):
    message: str

class ToxicChatResult(BaseModel):
    is_toxic: bool
    score: float

class ToxicChatResponse(BaseModel):
    result: ToxicChatResult

@router.post("/detect", response_model=ToxicChatResponse)
def detect_toxic_chat(request: ToxicChatRequest):
    """
    Detect toxic chat messages using a fine-tuned model.
    """
    result = recognize_toxic_chat(request.message)
    return ToxicChatResponse(result=result)
