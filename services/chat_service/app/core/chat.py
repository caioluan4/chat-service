# Arquivo: app/core/chat.py

import litellm
import os
import json
import time
import uuid
from app.rag.retriever import get_retriever

# Comando para o litellm descartar parametros nao suportados
litellm.drop_params = True

# Defina um timeout padrao para a chamada
DEFAULT_TIMEOUT = 30 # segundos



def chat(
    messages: list,
    model_alias: str,
    temperature: float = 0.2,
    top_p: float = 0.9,
    max_tokens: int = 512,
    seed: int = 42,
    stream: bool = False,
    json_mode: bool = False,
    timeout: int = DEFAULT_TIMEOUT,
    use_rag: bool = True
) -> dict:
    """
    Função principal que interage com os modelos de chat via LiteLLM.
    Pode opcionalmente usar RAG para enriquecer o contexto.
    """
    
    request_id = str(uuid.uuid4())[:8]

   
    if use_rag:
        if not messages or messages[-1].get("role") != "user":
            return {
                "error": {"code": "INVALID_INPUT", "message": "Para usar RAG, a última mensagem deve ser do usuário."},
                "request_id": request_id
            }

        query = messages[-1]["content"]

        # 1. Buscar contexto relevante no Qdrant
        retriever = get_retriever()
        retrieved_docs = retriever.get_relevant_documents(query)

        # 2. Formatar o contexto para incluir no prompt
        context = "\n\n".join([doc.page_content for doc in retrieved_docs])

        # 3. Criar o prompt aumentado (RAG) e substituir a lista de mensagens
        prompt_template = f"""Você é um assistente prestativo. Responda à pergunta do usuário com base apenas no seguinte contexto:

Contexto:
{context}

Pergunta: {query}"""
        
        # A lista de mensagens original é substituída pelo prompt do RAG
        messages = [{"role": "user", "content": prompt_template}]
    # ^-- FIM DO BLOCO RAG

    # RESOLVER MODEL_ALIAS
    config_path = os.path.join(os.path.dirname(__file__), '..', '..', 'config', 'models.json')
    
    try:
        with open(config_path, 'r') as f:
            config = json.load(f)
        
        model_info = config['aliases'][model_alias]
        provider = model_info['provider']
        model = model_info['model']
        
    except FileNotFoundError:
        return {
            "error": {"code": "CONFIG_ERROR", "message": "Config file not found"},
            "provider": None,
            "model": None,
            "request_id": request_id
        }
    except KeyError:
        return {
            "error": {"code": "MODEL_ALIAS_NOT_FOUND", "message": f"Model alias '{model_alias}' not found in config"},
            "provider": None,
            "model": None,
            "request_id": request_id
        }

    # CHAMAR O LITELLM E CAPTURAR AS MÉTRICAS
    start_time = time.time()
    
    try:
        litellm_model = f"{provider}/{model}"
        
        # Parâmetros unificados para a chamada
        params = {
            "model": litellm_model,
            "messages": messages,
            "temperature": temperature,
            "top_p": top_p,
            "max_tokens": max_tokens,
            "seed": seed,
            "stream": stream,
            "timeout": timeout 
        }

        # Adiciona o JSON mode se aplicável
        if json_mode:
            params["response_format"] = {"type": "json_object"}
            params["messages"].append({"role": "system", "content": "Return the response in JSON format."})
            
        response = litellm.completion(**params)
        
        latency_ms = (time.time() - start_time) * 1000

        # Extrair dados da resposta
        output_text = response.choices[0].message.content
        usage = response.usage
        effective_model = response.model
        effective_provider = response.model.split('/')[0]

        return {
            "output_text": output_text,
            "provider": effective_provider,
            "model": effective_model,
            "usage": {
                "prompt_tokens": usage.prompt_tokens,
                "completion_tokens": usage.completion_tokens,
                "total_tokens": usage.total_tokens
            },
            "latency_ms": int(round(latency_ms)),
            "cost_estimated": None,
            "request_id": request_id
        }
    # Tratamento de exceções específicas
    except litellm.exceptions.Timeout:
        return {
            "error": {"code": "TIMEOUT_ERROR", "message": "The request timed out."},
            "provider": provider,
            "model": model,
            "request_id": request_id
        }
    except litellm.exceptions.AuthenticationError:
        return {
            "error": {"code": "AUTH_ERROR", "message": "Authentication failed. Check your API key in .env"},
            "provider": provider,
            "model": model,
            "request_id": request_id
        }
    except Exception as e:
        return {
            "error": {"code": "PROVIDER_ERROR", "message": f"An error occurred with the provider: {e}"},
            "provider": provider,
            "model": model,
            "request_id": request_id
        }