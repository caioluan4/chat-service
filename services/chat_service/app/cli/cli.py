from dotenv import load_dotenv
load_dotenv()

import argparse
import json
import os
import sys

# Importa a lógica do core
from services.chat_service.app.core.chat import chat

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

    args = parser.parse_args()

    # Lógica de execução
    if args.command == "models":
        # Lógica para listar os modelos
        config_path = os.path.join(
            os.path.dirname(os.path.abspath(__file__)),
            '..', '..', 'config', 'models.json'
        )
        try:
            with open(config_path, "r") as f:
                models_config = json.load(f)
            
            print(json.dumps(models_config["aliases"], indent=2))
        except FileNotFoundError:
            print("Erro: Arquivo models.json não encontrado.")
        except KeyError:
            print("Erro: Estrutura inválida em models.json.")

    elif args.command == "chat":
        # Lógica para enviar o chat
        user_message = {"role": "user", "content": args.user}
        messages = [user_message]
        
        response = chat(
            messages=messages,
            model_alias=args.model
        )
        
        print(json.dumps(response, indent=2))

if __name__ == "__main__":
    main()