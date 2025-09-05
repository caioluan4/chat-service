# Chat Service com LiteLLM, FastAPI e CLI

Este projeto é um serviço de chat desenvolvido em Python. O objetivo é criar um serviço que possa alternar entre diferentes provedores de modelos de IA (como Groq e Fireworks) de forma transparente, usando a biblioteca LiteLLM. O serviço é exposto via uma API HTTP (FastAPI) e uma interface de linha de comando (CLI).

## Estrutura de Diretórios

O projeto segue a seguinte estrutura, com separação de responsabilidades:

- `app/`: Contém o código da aplicação (core, api, cli).
- `config/`: Arquivos de configuração, como o mapeamento de modelos (`models.json`).
- `prompts/`: Prompts de validação em arquivos de texto.
- `runs/`: Pasta para logs e telemetria gerados em tempo de execução.
- `.env.example`: Modelo para variáveis de ambiente.
- `README.md`: Documentação deste serviço.

## Dependências Mínimas

As bibliotecas necessárias para o projeto podem ser instaladas com o seguinte comando:

```bash
pip install litellm fastapi uvicorn