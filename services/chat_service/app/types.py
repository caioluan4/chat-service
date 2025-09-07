from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional

class ChatMessage(BaseModel):
    role: str
    content: str

class ChatParams(BaseModel):
    temperature: float = 0.2
    top_p: float = 0.9
    max_tokens: int = 512
    seed: Optional[int] = 42
    stream: bool = False
    json_mode: bool = False

class ChatRequest(BaseModel):
    model: str
    messages: List[ChatMessage]
    params: Optional[ChatParams] = ChatParams()

class ChatUsage(BaseModel):
    prompt_tokens: int
    completion_tokens: int
    total_tokens: int

class ChatResponse(BaseModel):
    ts: Optional[str] = None
    run_id: Optional[str] = None
    request_id: Optional[str] = None
    provider: str
    model: str
    params: Optional[Dict[str, Any]] = None # Adicione este campo
    usage: ChatUsage
    latency_ms: float
    cost_estimated: Optional[float] = None
    status: str = "ok"
    error: Optional[Dict[str, Any]] = None
    output_text: Optional[str] = None
    messages: Optional[List[Dict[str, Any]]] = None