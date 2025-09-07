# Arquivo: services/chat_service/app/cli/cli.py

import argparse
import json
import os
import sys
import uuid
import time
from datetime import datetime
import subprocess

# Garante que o diretório raiz do projeto esteja no sys.path para que os imports funcionem corretamente
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..')))

# Carrega as variáveis de ambiente do arquivo .env
from dotenv import load_dotenv
load_dotenv()

# Importa os tipos Pydantic
from services.chat_service.app.types import ChatResponse

# Importa a lógica do core
from services.chat_service.app.core.chat import chat

def save_manifest(manifest_data: dict, run_id: str):
    """
    Salva o arquivo manifest.json com metadados do run.
    """
    runs_dir = os.path.join(
        os.path.dirname(os.path.abspath(__file__)),
        '..', '..', 'runs', run_id
    )
    os.makedirs(runs_dir, exist_ok=True)
    
    file_path = os.path.join(runs_dir, "manifest.json")
    
    with open(file_path, "w") as f:
        json.dump(manifest_data, f, indent=2)

def save_metrics(data: dict, run_id: str):
    """
    Salva as métricas de uma interação em um arquivo JSONL.
    """
    runs_dir = os.path.join(
        os.path.dirname(os.path.abspath(__file__)),
        '..', '..', 'runs', run_id
    )
    os.makedirs(runs_dir, exist_ok=True)
    
    file_path = os.path.join(runs_dir, "interactions.jsonl")
    
    # Valida os dados usando o modelo Pydantic antes de salvar
    try:
        validated_data = ChatResponse(**data).model_dump()
        with open(file_path, "a") as f:
            f.write(json.dumps(validated_data) + "\n")
    except Exception as e:
        print(f"Erro de validação ao salvar métricas: {e}")

def main():
    """
    Função principal da CLI
    """
    parser = argparse.ArgumentParser(description="CLI para o serviço de chat do Eldorado.")
    subparsers = parser.add_subparsers(dest="command", help="Comandos disponíveis")

    # Comando 'models'
    models_parser = subparsers.add_parser("models", help="Lista os modelos de chat disponíveis.")

    # Comando 'chat'
    chat_parser = subparsers.add_parser("chat", help="Envia um prompt para o serviço de chat.")
    chat_parser.add_argument("--model", required=True, help="Alias do modelo a ser usado (ex: chat/llama-small).")
    chat_parser.add_argument("--user", required=True, help="Prompt do usuário.")
    chat_parser.add_argument("--system", required=False, help="Prompt para o sistema.")

    chat_parser.add_argument("--temperature", type=float, default=0.2, help="Parâmetro de temperatura para o modelo.")
    chat_parser.add_argument("--max-tokens", type=int, default=512, help="Número máximo de tokens a serem gerados.")

    args = parser.parse_args()

    # Gera um ID de execução único
    run_id = f"{datetime.utcnow().strftime('%Y-%m-%dT%H-%M-%SZ')}_{str(uuid.uuid4())[:8]}"

    # Adiciona a lógica para carregar aliases
    aliases_loaded = []
    config_path = os.path.join(
        os.path.dirname(os.path.abspath(__file__)),
        '..', '..', 'config', 'models.json'
    )
    try:
        with open(config_path, "r") as f:
            models_config = json.load(f)
            aliases_loaded = list(models_config.get("aliases", {}).keys())
    except FileNotFoundError:
        print("Erro: Arquivo models.json não encontrado. Verifique a estrutura.")
    except KeyError:
        print("Erro: Estrutura inválida em models.json.")

    # Tenta obter o git SHA
    git_sha = ""
    try:
        git_sha = subprocess.check_output(['git', 'rev-parse', 'HEAD']).strip().decode('utf-8')
    except (subprocess.CalledProcessError, FileNotFoundError):
        git_sha = "<hash>" # Valor padrão se o comando falhar

    # Informações de pacotes (exemplo, idealmente obtido dinamicamente)
    packages = {
        "litellm": "x.y.z",
        "fastapi": "x.y.z"
    }

    # Dados completos para o manifest.json
    manifest_data = {
        "run_id": run_id,
        "service": "chat_service",
        "started_at": datetime.utcnow().isoformat(),
        "git_sha": git_sha,
        "python_version": f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}",
        "packages": packages,
        "aliases_loaded": aliases_loaded
    }

    save_manifest(manifest_data, run_id)

    # Lógica de execução
    if args.command == "models":
        config_path = os.path.join(
            os.path.dirname(os.path.abspath(__file__)),
            '..', '..', 'config', 'models.json'
        )
        try:
            with open(config_path, "r") as f:
                models_config = json.load(f)
            
            print(json.dumps(models_config["aliases"], indent=2))
        except FileNotFoundError:
            print("Erro: Arquivo models.json não encontrado. Verifique a estrutura.")
        except KeyError:
            print("Erro: Estrutura inválida em models.json.")

    elif args.command == "chat":
        messages = []
        # Adiciona a mensagem do sistema se o argumento for fornecido
        if args.system:
            messages.append({"role": "system", "content": args.system})

        user_message = {"role": "user", "content": args.user}
        messages.append(user_message)
        
        request_id = str(uuid.uuid4())[:8]
        
        # Chama a função do core
    
        response = chat(
        messages=messages,
        model_alias=args.model,
        temperature=args.temperature, 
        max_tokens=args.max_tokens, 
       
    )
        
        # Prepara os dados para salvar
        metrics_data = {
            "ts": datetime.utcnow().isoformat(),  # Adicione o timestamp
            "run_id": run_id, # Adicione o run_id
            "request_id": request_id,
            "provider": response.get("provider"),
            "model": response.get("model"),
            "params": {
            "temperature": args.temperature, 
            "top_p": 0.9,
            "max_tokens": args.max_tokens, 
            "json_mode": False
        },
            "usage": response.get("usage"),
            "latency_ms": response.get("latency_ms"),
            "status": "ok" if "error" not in response else "error",
            "cost_estimated": response.get("cost_estimated")
        }
        
        # Adiciona mensagens e output_text se LOG_MESSAGES for true
        if os.getenv("LOG_MESSAGES", "").lower() == "true":
            metrics_data["messages"] = messages
            metrics_data["output_text"] = response.get("output_text")

        save_metrics(metrics_data, run_id)
        
        try:
            
            print(json.dumps(response, indent=2))
        except Exception as e:
            print(f"Erro ao imprimir a resposta: {e}")

if __name__ == "__main__":
    main()