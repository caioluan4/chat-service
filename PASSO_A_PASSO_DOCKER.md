# 🚀 Passo a Passo para Dockerizar o Chat Service (FastAPI) em Dupla

Este guia foi feito para que **duas pessoas** dockerizem juntas o projeto **Chat Service** (Python + FastAPI + CLI).
Ele contém a divisão de tarefas, arquivos prontos, comandos de validação, critérios de aceite, **boas práticas** e troubleshooting.

> **Contexto do projeto**
> - API FastAPI com entrypoint: `services.chat_service.app.api.main:app`
> - Execução local padrão: `uvicorn services.chat_service.app.api.main:app --reload`
> - Porta padrão interna: **8000**
> - Endpoints: `/healthz`, `/models`, `/chat`
> - CLI: `python -m services.chat_service.app.cli.cli`
> - `.env.example` já existe no projeto (preencha seu `.env` fora do Git)

---

## ✅ Pré‑requisitos
- Docker 24+ e Docker Compose v2+
- Arquivo `.env` baseado no seu `.env.example` (não commitar!)
- `models.json` em `services/chat_service/config/`

Sugestão mínima de `requirements.txt` (ajuste conforme seu projeto):
```txt
fastapi
uvicorn[standard]
litellm
python-dotenv
```

---

## 👤 Pessoa 1 — **Container da Aplicação**
**Objetivo:** empacotar a API/CLI em uma imagem leve e segura, que rode com `docker run`.

### 1) Criar `.dockerignore`
```gitignore
.git
.gitignore
.vscode
.idea
__pycache__/
*.pyc
*.log
.env
.env.*
.venv
venv
dist
build
.DS_Store
node_modules
```

### 2) Criar `Dockerfile`
```dockerfile
# syntax=docker/dockerfile:1.7
FROM python:3.12-slim AS base
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    PORT=8000
WORKDIR /app

# Instala dependências (use requirements.txt ou adapte para pyproject/poetry)
COPY requirements.txt .
RUN --mount=type=cache,target=/root/.cache/pip \
    pip install --upgrade pip && pip install -r requirements.txt

# Copia o código
COPY . .

# Usuário não-root (segurança)
RUN useradd -m appuser
USER appuser

# A API interna usa 8000 por padrão (Uvicorn)
EXPOSE 8000

# Healthcheck simples sem curl/wget
HEALTHCHECK --interval=30s --timeout=5s --retries=3 CMD python -c "import urllib.request; urllib.request.urlopen('http://127.0.0.1:8000/healthz', timeout=3)"

# Comando padrão (produção)
CMD ["python", "-m", "uvicorn", "services.chat_service.app.api.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

### 3) Build & Run (validação)
```bash
# Build
docker build -t chat-service:local .

# Run (host:container); mude a porta do host se quiser (ex.: 8080:8000)
docker run --rm -p 8000:8000 --env-file .env chat-service:local

# Teste de saúde
curl http://127.0.0.1:8000/healthz
```

### 4) Testar a **CLI** dentro do container
```bash
# Descobrir container id (em outro terminal)
docker ps

# Executar CLI
docker exec -it <CONTAINER_ID> \
  python -m services.chat_service.app.cli.cli models
```

### ✅ Critérios de aceite (Pessoa 1)
- `docker build` finaliza sem erros.
- `docker run` responde `200 OK` em `GET /healthz`.
- CLI funciona via `docker exec`.

---

## 👤 Pessoa 2 — **Orquestração com Docker Compose**
**Objetivo:** padronizar execução com Compose, incluindo perfis **dev** (hot-reload) e **prod** (imagem imutável), além de volumes para `config/` e `runs/`.

### 1) Criar `docker-compose.yml`
```yaml
version: "3.9"

services:
  # Desenvolvimento: hot-reload e bind mount do código
  chat-service:
    build:
      context: .
      dockerfile: Dockerfile
    image: chat-service:dev
    env_file:
      - .env
    ports:
      - "8000:8000"   # mude para "8080:8000" se preferir no host
    volumes:
      - .:/app
      - ./services/chat_service/runs:/app/services/chat_service/runs
      - ./services/chat_service/config:/app/services/chat_service/config:ro
    command: >
      python -m uvicorn services.chat_service.app.api.main:app \
      --host 0.0.0.0 --port 8000 --reload
    healthcheck:
      test: ["CMD-SHELL", "python -c 'import urllib.request; urllib.request.urlopen(\"http://127.0.0.1:8000/healthz\", timeout=3)' "]
      interval: 30s
      timeout: 5s
      retries: 3
    restart: unless-stopped
    profiles: ["dev"]

  # Produção: sem bind do código, sem reload
  chat-service-prod:
    build:
      context: .
      dockerfile: Dockerfile
    image: chat-service:prod
    env_file:
      - .env
    ports:
      - "8000:8000"
    volumes:
      - ./services/chat_service/runs:/app/services/chat_service/runs
      - ./services/chat_service/config:/app/services/chat_service/config:ro
    command: >
      python -m uvicorn services.chat_service.app.api.main:app \
      --host 0.0.0.0 --port 8000 --workers 1
    restart: unless-stopped
    profiles: ["prod"]
```

### 2) Subir e validar (dev)
```bash
# Sobe com hot-reload
docker compose --profile dev up -d

# Logs
docker compose --profile dev logs -f chat-service

# Health
curl http://127.0.0.1:8000/healthz

# CLI via compose
docker compose --profile dev exec chat-service \
  python -m services.chat_service.app.cli.cli models
```

### 3) Subir e validar (prod)
```bash
# Sobe produção (sem reload)
docker compose --profile prod up -d

docker compose --profile prod logs -f chat-service-prod
curl http://127.0.0.1:8000/healthz
```

### ✅ Critérios de aceite (Pessoa 2)
- `docker compose --profile dev up -d` e `--profile prod up -d` sobem sem erros.
- Bind mount em dev com `--reload` funciona (editar código → API reinicia).
- Volumes: `config/` (somente leitura) e `runs/` (persistente) estão montados.

---

## 🔄 Validação cruzada (ambos)
- **API:** `GET /healthz` → `200 OK`
- **Models:** `GET /models` retorna os aliases configurados no `models.json`.
- **Chat:** `POST /chat` responde com JSON de saída e métricas.
- **CLI:** `models` e `chat` funcionam dentro do container.

---

## 🧠 Boas Práticas (recomendadas)

### Segurança
- Rode como **usuário não‑root** (`USER appuser`) no container.
- Não commite **segredos**: use `.env` local e **secrets** no CI/CD.

### Reprodutibilidade
- **Fixe versões** no `requirements.txt` e na imagem base (`python:3.12-slim`).
- Use `--mount=type=cache` no pip (já incluído) para builds rápidos.

### Imagem enxuta
- Use imagens base **slim** e evite ferramentas desnecessárias.
- Mantenha `.dockerignore` atualizado para não copiar lixo para a imagem.

### Observabilidade
- Tenha endpoint de **health** (`/healthz`) e **healthcheck** no Docker/Compose.
- Mapeie `services/chat_service/runs` para persistir **telemetria/métricas**.

### Config & dados
- Monte `services/chat_service/config` como **somente leitura** (evita sobrescrita).
- Centralize **variáveis de ambiente** via `env_file` no Compose.

### Redes e portas
- Mantenha a **porta interna** fixa (8000) e ajuste a **externa** no host (ex.: `8080:8000`).
- Evite colisões de porta no host quando subir múltiplas instâncias.

### Execução
- Em **dev**: bind mount + `--reload` para produtividade.
- Em **prod**: sem bind mount, sem `--reload`, imagem imutável.

### CI/CD (quando chegar a hora)
- Use GitHub Actions para build multi‑arch (`amd64`, `arm64`) e push para GHCR ou Docker Hub.
- Tagueie imagens com `sha`, `semver` e `latest`.

---

## 🛠️ Troubleshooting rápido
- **Não sobe/404:** confira se o comando aponta para `services.chat_service.app.api.main:app`.
- **Healthcheck falha:** verifique `.env` e `models.json` em `config/`.
- **Permissões em `runs/`:** se necessário, crie a pasta no host (`mkdir -p services/chat_service/runs`) antes do `up`.
- **Porta ocupada:** troque para `8080:8000` no `ports`.

---

## 📌 Referência de comandos
```bash
# Build e run simples (sem compose)
docker build -t chat-service:local .
docker run --rm -p 8000:8000 --env-file .env chat-service:local

# Compose DEV
docker compose --profile dev up -d
docker compose --profile dev logs -f chat-service

# Compose PROD
docker compose --profile prod up -d
docker compose --profile prod logs -f chat-service-prod

# Testes
curl http://127.0.0.1:8000/healthz
curl http://127.0.0.1:8000/models

# CLI
docker compose --profile dev exec chat-service \
  python -m services.chat_service.app.cli.cli models
```

---

## ✅ Checklist de PRs
**Pessoa 1 — `feature/dockerfile-app`**
- [ ] `.dockerignore`
- [ ] `Dockerfile` com usuário não‑root e healthcheck
- [ ] `docker run` responde `200` em `/healthz`
- [ ] CLI funcional via `docker exec`

**Pessoa 2 — `feature/compose-env`**
- [ ] `docker-compose.yml` com perfis `dev`/`prod`
- [ ] Volumes para `config` (ro) e `runs`
- [ ] Healthcheck no serviço
- [ ] Documentação de como subir/validar
