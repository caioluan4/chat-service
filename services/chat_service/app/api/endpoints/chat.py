# services/chat_service/app/api/endpoints/chat.py

from fastapi import APIRouter
from pydantic import BaseModel
from app.core.chat import chat as chat_logic 

# ✅ Garanta que esta linha existe!
router = APIRouter() 

class ChatRequest(BaseModel):
    message: str
    model_alias: str = "gemma2"

@router.post("/chat")
async def handle_chat(request: ChatRequest):
    messages = [{"role": "user", "content": request.message}]
    
    # Chame a função de lógica que foi renomeada
    response_data = chat_logic(messages=messages, model_alias=request.model_alias)
    
    response_text = response_data.get("output_text")
    if response_text is None:
        return {"error": response_data.get("error", "Unknown error")}

    return {"response": response_text}