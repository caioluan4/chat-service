# Chat Service com LiteLLM, FastAPI e CLI

Este projeto é um serviço de chat desenvolvido em **Python**.  
O objetivo é criar um serviço que possa alternar entre diferentes provedores de modelos de IA (como **Groq** e **Fireworks**) de forma transparente, usando a biblioteca **LiteLLM**.  
O serviço é exposto via uma **API HTTP (FastAPI)** e uma **interface de linha de comando (CLI)**.

---

## 📂 Estrutura de Diretórios

O projeto segue a seguinte estrutura, com separação de responsabilidades:

```
services/chat_service/
├── app/              # Código da aplicação (core, api, cli)
├── config/           # Arquivos de configuração (models.json, etc.)
├── prompts/          # Prompts de validação em arquivos de texto
├── runs/             # Logs e telemetria em tempo de execução
├── .env.example      # Modelo para variáveis de ambiente
├── README.md         # Documentação do serviço
```

> Obs.: Lembre-se de adicionar `__init__.py` nas pastas `chat_service/` e `app/` para que sejam reconhecidas como pacotes Python.

---

## 📦 Dependências Mínimas

Instale as bibliotecas necessárias com:

```bash
pip install litellm fastapi uvicorn python-dotenv
```

---

## ⚙️ Passo a Passo para Setup e Execução

### 1. Configuração do Ambiente

1. Crie um arquivo **.env** em `services/chat_service/` com suas chaves de API:

   ```env
   GROQ_API_KEY=sua_chave_groq
   FIREWORKS_AI_API_KEY=sua_chave_fireworks
   ```

2. Crie o arquivo **models.json** em `config/` com os aliases:

   ```json
   {
     "aliases": {
       "chat/llama-small": {
         "provider": "groq",
         "model": "llama-3.1-8b-instant"
       },
       "chat/qwen-small": {
         "provider": "fireworks_ai",
         "model": "accounts/fireworks/models/qwen2p5-vl-32b-instruct"
       }
     }
   }
   ```

---

### 2. Rodar a API

Na raiz do projeto (`/repo`), execute:

```bash
uvicorn services.chat_service.app.api.main:app --reload
```

O servidor iniciará na **porta 8000**.  
Deixe este terminal rodando.

---

### 3. Testar os Endpoints

Abra outro terminal e rode os testes abaixo:

#### 🔹 Health Check

```bash
curl http://127.0.0.1:8000/healthz
```

**Resposta esperada:**

```json
{"status":"ok"}
```

---

#### 🔹 Listar Modelos

```bash
curl http://127.0.0.1:8000/models
```

**Resposta esperada:**  
Lista dos aliases definidos no `models.json`.

---

#### 🔹 Chat

```bash
curl -X POST http://127.0.0.1:8000/chat -H "Content-Type: application/json" -d '{
  "model": "chat/llama-small",
  "messages": [
    {
      "role": "user",
      "content": "Explique, em ate 120 palavras, o que e consistencia eventual e cite 1 caso de uso comum."
    }
  ],
  "params": {
    "temperature": 0.2,
    "top_p": 0.9,
    "max_tokens": 512,
    "seed": 42,
    "stream": false,
    "json_mode": false
  }
}'
```

**Resposta esperada:**  
Um JSON contendo:
- Texto de saída
- Provedor e modelo usados
- Métricas de uso
- Latência



---

## 🖥️ Usar a CLI

A **CLI** permite interagir com o serviço diretamente do terminal.

Na raiz do projeto (`/repo`), use o comando `python -m` para executar a CLI.

### 🔹 Listar Modelos

```bash
python -m services.chat_service.app.cli.cli models
```

**Resposta esperada:**  
A lista de aliases do seu `models.json`.

---

### 🔹 Chat

```bash
python -m services.chat_service.app.cli.cli chat --model chat/llama-small --user "Explique o que e consistencia eventual."
```

**Resposta esperada:**  
Um JSON com:
- A resposta do modelo
- Métricas
- Uso de tokens

---



## ⚡ Política Assíncrona (Async)

O serviço de chat foi projetado para ser responsivo e não bloqueante. Para isso, seguimos a seguinte política:

* **Lógica do Core**: A função `chat` em `app/core/chat.py` é **síncrona**. Ela lida com a lógica de chamada à API do LiteLLM de forma simples e direta.
* **API FastAPI**: O endpoint `POST /chat` é **assíncrono** (`async`). Ele usa o utilitário `asyncio.to_thread` para executar a função síncrona do core em um thread separado.

Essa abordagem garante que a API não seja bloqueada por chamadas de longa duração ao modelo de IA, permitindo que ela processe outras requisições em paralelo e mantendo a alta performance do serviço.



## ✅ Validação de Startup

O serviço executa uma série de verificações automáticas na inicialização para garantir que o ambiente está configurado corretamente. A validação inclui:

* Checagem do arquivo `models.json`.
* Verificação das chaves de API necessárias no `.env`.
* Um ping leve em cada provedor configurado para validar a conexão e a autenticação.

Se alguma dessas validações falhar, o serviço não iniciará e exibirá uma mensagem de erro clara no terminal.

---

## 📊 Métricas e Telemetria

O serviço gera logs e métricas de telemetria em tempo de execução na pasta `runs/`.

* **`manifest.json`**: Este arquivo de metadados é gerado por execução (`run_id`). Ele registra informações sobre o ambiente, como o hash do Git (`git_sha`), a versão do Python e as dependências.
* **`interactions.jsonl`**: Este é o arquivo principal de logs, onde cada linha é um JSON contendo os dados de uma interação com o modelo de chat. Ele inclui métricas como `latency_ms` e `usage.total_tokens` para cada requisição.

Você pode habilitar o log completo da conversa (mensagens de entrada e saída) definindo a variável `LOG_MESSAGES` no seu arquivo `.env`:

```env
LOG_MESSAGES=true