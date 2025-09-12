# services/chat_service/app/api/endpoints/chat.py
from fastapi import APIRouter
from pydantic import BaseModel
from app.core.chat import get_rag_response

router = APIRouter()

class ChatRequest(BaseModel):
    message: str

@router.post("/chat")
async def handle_chat(request: ChatRequest):
    response_text = get_rag_response(request.message)
    return {"response": response_text}