# Arquivo: app/api/main.py

from dotenv import load_dotenv
load_dotenv()

from pydantic import BaseModel, Field, conlist
from typing import List, Dict, Any, Optional
from fastapi import FastAPI, HTTPException
from typing import Dict, Any
import json
import os


from services.chat_service.app.core.startup import validate_startup

# Importa to_thread para usar a política assíncrona
import asyncio


# Importa os modelos Pydantic de types
from services.chat_service.app.types import ChatRequest, ChatResponse, ChatMessage

# Importa a lógica do core
from services.chat_service.app.core.chat import chat

# Cria a instância da sua aplicação FastAPI
app = FastAPI()

# Executa a validação na inicialização do serviço
validate_startup()




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
async def chat_endpoint(request: ChatRequest) -> ChatResponse:
    """
    Recebe uma requisição de chat e retorna a resposta do modelo de IA.
    """
    
    response = await asyncio.to_thread(
        chat,
        messages=[m.model_dump() for m in request.messages],
        model_alias=request.model,
        **request.params.model_dump() if request.params else {}
    )

    return ChatResponse(**response)

