import litellm
import os
import json
import time


def chat(
    messages: list,
    model_alias: str,
    temperature: float = 0.2,
    top_p: float = 0.9,
    max_tokens: int = 512,
    seed: int = 42,
    stream: bool = False,
    json_mode: bool = False
) -> dict:
    """
    Função principal que interage com os modelos de chat via LiteLLM.
    """
    
    # RESOLVER MODEL_ALIAS 
    # Caminho para o arquivo models.json
    config_path = os.path.join(os.path.dirname(__file__), '..', '..', 'config', 'models.json')
    
    try:
        with open(config_path, 'r') as f:
            config = json.load(f)
        
        # Procura o alias no dicionário
        model_info = config['aliases'][model_alias]
        provider = model_info['provider']
        model = model_info['model']
        
        # Combina provedor e modelo para a chamada do LiteLLM
        litellm_model = f"{provider}/{model}"
        
    except FileNotFoundError:
        # Erro se o arquivo models.json não for encontrado
        return {"error": "Config file not found"}
    except KeyError:
        # Erro se o alias não for encontrado no arquivo
        return {"error": f"Model alias '{model_alias}' not found in config"}

    #CHAMAR O LITELLM E CAPTURAR AS MÉTRICAS 

    start_time = time.time()
    try:
        response = litellm.completion(
            model=litellm_model,
            messages=messages,
            temperature=temperature,
            top_p=top_p,
            max_tokens=max_tokens,
            seed=seed,
            stream=False,
            #json_mode=json_mode
        )
        latency_ms = (time.time() - start_time) * 1000

        # Extrair dados da resposta
        output_text = response.choices[0].message.content
        usage = response.usage
        effective_model = response.model
        effective_provider = response.model.split('/')[0] # Extrai o provedor do nome do modelo

    except litellm.exceptions.AuthenticationError:
        return {"error": "Authentication failed. Check your API key in .env"}
    except Exception as e:
        return {"error": f"An error occurred: {e}"}

    # RETORNAR O RESULTADO FINAL
    return {
        "output_text": output_text,
        "provider": effective_provider,
        "model": effective_model,
        "usage": {
            "prompt_tokens": usage.prompt_tokens,
            "completion_tokens": usage.completion_tokens,
            "total_tokens": usage.total_tokens
        },
        "latency_ms": round(latency_ms, 2),
        "cost_estimated": None
    }
   