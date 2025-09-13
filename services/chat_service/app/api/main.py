# services/chat_service/app/api/main.py

import os
import json
from fastapi import FastAPI, HTTPException
from dotenv import load_dotenv

# Carrega as variáveis de ambiente do .env
load_dotenv()

# 1. Importa APENAS os módulos de endpoints
from .endpoints import ingest, chat
from app.core.startup import validate_startup

# Cria a instância da sua aplicação FastAPI
app = FastAPI(title="Chat Service com RAG")

# Executa a validação na inicialização do serviço
validate_startup()

# 2. Inclui os routers dos módulos importados
app.include_router(chat.router, prefix="/api")
app.include_router(ingest.router, prefix="/api")

# --- Endpoints que pertencem ao main.py ---

@app.get("/", tags=["Status"])
def read_root():
    return {"status": "Serviço de Chat com RAG está no ar!"}

@app.get("/healthz", tags=["Status"])
def healthz():
    """Retorna o status de saúde do serviço."""
    return {"status": "ok"}

@app.get("/models", tags=["Models"])
def get_models():
    """Retorna a lista de modelos disponíveis."""
    config_path = os.path.join(
        os.path.dirname(__file__), '..', '..', 'config', 'models.json'
    )
    try:
        with open(config_path, "r") as f:
            models_config = json.load(f)
        return models_config.get("aliases", {})
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail="models.json not found")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

