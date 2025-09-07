
import os
import json
import litellm
from dotenv import load_dotenv

# Garante que as variáveis de ambiente estão carregadas antes de qualquer validação.
load_dotenv()

def validate_startup():
    """
    Executa todas as validações de startup para o serviço de chat.
    """
    print("Iniciando validação de startup...")

    # 1. Validação do arquivo de configuração de modelos
    config_path = os.path.join(
        os.path.dirname(os.path.abspath(__file__)),
        '..', '..', 'config', 'models.json'
    )
    
    try:
        with open(config_path, "r") as f:
            models_config = json.load(f)
        aliases = models_config.get("aliases", {})
        if not aliases:
            raise ValueError("No aliases found in models.json")
    except FileNotFoundError:
        raise FileNotFoundError(f"models.json not found at {config_path}. Please check your project structure.")
    except (json.JSONDecodeError, ValueError) as e:
        raise RuntimeError(f"Error parsing models.json: {e}")

    # 2. Validação das chaves de ambiente e ping nos provedores
    providers = set(info['provider'] for info in aliases.values())
    
    for provider in providers:
        api_key_name = f"{provider.upper()}_API_KEY"
        if not os.getenv(api_key_name):
            raise RuntimeError(f"API key for provider '{provider}' not found. Please set {api_key_name} in your .env file.")

        print(f"Validando conexão com o provedor: {provider}...")
        
        # Ping leve para validar a autenticação.
        # Usa um modelo leve e uma requisição mínima.
        try:
            # Exemplo com uma chamada leve ao provedor
            # A LiteLLM suporta o parametro `mock_response` para não chamar a API real
            # No entanto, vamos fazer uma chamada real para validar a chave de API
            test_model = f"{provider}/gpt-3.5-turbo" # Exemplo de modelo, pode ser outro
            if provider == "groq":
                test_model = "groq/llama-3.1-8b-instant"
            elif provider == "fireworks_ai":
                test_model = "fireworks_ai/accounts/fireworks/models/qwen2p5-vl-32b-instruct"
            
            litellm.completion(
                model=test_model,
                messages=[{"role": "user", "content": "ping"}],
                mock_response="pong"
            )
            print(f"Conexão com '{provider}' bem-sucedida.")
        except Exception as e:
            raise RuntimeError(f"Failed to connect to provider '{provider}'. Check your API key and network connection. Error: {e}")
            
    print("Validação de startup concluída com sucesso!")