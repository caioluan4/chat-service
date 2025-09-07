from dotenv import load_dotenv
load_dotenv()


from fastapi import FastAPI
from pydantic import BaseModel, Field, conlist
from typing import List, Dict, Any, Optional
import json
import os


# Importa a lógica do core
from services.chat_service.app.core.chat import chat

# Cria a instância da sua aplicação FastAPI
app = FastAPI()

# Definição do esquema de dados da requisição
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


# Endpoint para checagem de saúde
@app.get("/healthz")
def healthz():
    """
    Retorna o status do serviço.
    """
    return {"status": "ok"}

# Endpoint para checagem dos modelos disponiveis
@app.get("/models")
def get_models():
    """
    Retorna a lista de aliases e suas resoluções do arquivo models.json.
    """
    # Define o caminho para o arquivo de configuração de forma relativa.
    # A partir da localização do main.py, volta duas pastas e entra em 'config'
    config_path = os.path.join(
        os.path.dirname(__file__), '..', '..', 'config', 'models.json'
    )
    
    try:
        # Abre e lê o arquivo models.json.
        with open(config_path, "r") as f:
            models_config = json.load(f)
        
        # Retorna o dicionário de aliases
        return models_config.get("aliases", {})
    
    except FileNotFoundError:
        # Lança uma exceção HTTP 404 se o arquivo não for encontrado
        raise HTTPException(status_code=404, detail="models.json not found")
    except Exception as e:
        # Lança uma exceção HTTP 500 para outros erros
        raise HTTPException(status_code=500, detail=f"An error occurred: {e}")

    


# Endpoint para o chat
@app.post("/chat")
def chat_endpoint(request: ChatRequest) -> Dict[str, Any]:
    """
    Recebe uma requisição de chat e retorna a resposta do modelo de IA.
    """
    # Chama a função de chat do core
    response = chat(
        messages=[m.dict() for m in request.messages],
        model_alias=request.model,
        **request.params.dict()
    )

    return response