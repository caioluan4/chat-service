# Makefile para Gerenciamento do Projeto Docker

# -- Variáveis --
# Usar variáveis torna o Makefile mais fácil de manter.
IMAGE_NAME := chat-service
IMAGE_TAG := local

# Comandos base para cada ambiente, evitando repetição.
DEV_COMPOSE := docker compose -f docker/docker-compose.yml --profile dev
PROD_COMPOSE := docker compose -f docker/docker-compose.yml --profile prod
DEV_SERVICE_NAME := chat-service
PROD_SERVICE_NAME := chat-service-prod

# -- Alvos (Targets) --
# .PHONY garante que o 'make' execute o comando em vez de procurar um arquivo com o mesmo nome.
.PHONY: help build run up down logs exec prod-up prod-down prod-logs test-health test-models prune

# O alvo padrão, executado quando você digita apenas 'make'.
default: help

## 🐳 Docker Avulso

build: ## Constroi a imagem Docker localmente.
	@echo "🏗️  Construindo imagem $(IMAGE_NAME):$(IMAGE_TAG)..."
	@docker build -t $(IMAGE_NAME):$(IMAGE_TAG) -f docker/Dockerfile .

run: ## Executa o contêiner Docker avulso (requer .env).
	@echo "▶️  Executando contêiner $(IMAGE_NAME):$(IMAGE_TAG)..."
	@docker run --rm -p 8000:8000 -d --env-file .env $(IMAGE_NAME):$(IMAGE_TAG)

## -----------------------------------------------------------------------------
## 🛠️  Docker Compose (Desenvolvimento)
## -----------------------------------------------------------------------------

dev-up: ## Inicia os serviços de desenvolvimento em background.
	@echo "🚀 Iniciando ambiente de desenvolvimento..."
	@$(DEV_COMPOSE) up -d

dev-down: ## Para e remove os serviços de desenvolvimento.
	@echo "🛑 Parando ambiente de desenvolvimento..."
	@$(DEV_COMPOSE) down

dev-logs: ## Exibe os logs do serviço de desenvolvimento em tempo real.
	@echo "📄 Visualizando logs de $(DEV_SERVICE_NAME)..."
	@$(DEV_COMPOSE) logs -f $(DEV_SERVICE_NAME)

# Permite executar comandos dentro do contêiner. O padrão é abrir um shell.
# Exemplo de uso: make exec cmd="python -V"
cmd := bash
dev-exec: ## Executa um comando no contêiner. Ex: make exec cmd="ls -la"
	@echo "💻 Executando comando no contêiner $(DEV_SERVICE_NAME)..."
	@$(DEV_COMPOSE) exec $(DEV_SERVICE_NAME) $(cmd)

## -----------------------------------------------------------------------------
## 🚀 Docker Compose (Produção)
## -----------------------------------------------------------------------------

prod-up: ## Inicia os serviços de produção em background.
	@echo "🚀🚀 Iniciando ambiente de produção..."
	@$(PROD_COMPOSE) up -d

prod-down: ## Para e remove os serviços de produção.
	@echo "🛑🛑 Parando ambiente de produção..."
	@$(PROD_COMPOSE) down

prod-logs: ## Exibe os logs do serviço de produção em tempo real.
	@echo "📄 Visualizando logs de $(PROD_SERVICE_NAME)..."
	@$(PROD_COMPOSE) logs -f $(PROD_SERVICE_NAME)

## -----------------------------------------------------------------------------
## 📡 Testes da API
## -----------------------------------------------------------------------------

test-health: ## Executa o health check da API.
	@echo "🩺 Verificando health check em http://127.0.0.1:8000/healthz"
	@curl -s -o /dev/null -w "%{http_code}\n" http://127.0.0.1:8000/healthz

test-models: ## Lista os modelos disponíveis na API.
	@echo "🤖 Listando modelos em http://127.0.0.1:8000/models"
	@curl http://127.0.0.1:8000/models

## -----------------------------------------------------------------------------
## 🧹 Limpeza e Ajuda
## -----------------------------------------------------------------------------

prune: ## Limpa todos os recursos Docker não utilizados (cuidado!).
	@echo "🧹 Limpando sistema Docker..."
	@docker system prune -af

help: ## Exibe esta mensagem de ajuda.
	@echo "Comandos disponíveis:"
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-20s\033[0m %s\n", $$1, $$2}'

## -----------------------------------------------------------------------------
## 💬 Testes de Chat
## -----------------------------------------------------------------------------

# Variáveis para os comandos de chat.
# Você pode sobrescrevê-las na linha de comando.
# Ex: make chat MODEL="chat/qwen-small" PROMPT="Qual a capital do Brasil?" TEMP=0.8
MODEL ?= chat/llama-small
PROMPT ?= "Explique o que e consistencia eventual em ate 120 palavras e cite 1 caso de uso."
TEMP ?= 0.2
MAX_TOKENS ?= 512
SYSTEM_PROMPT ?= "" # Por padrão, não há prompt de sistema. Preencha para usar.

test-chat-api: ## Envia uma mensagem para o endpoint /chat via API com todos os parâmetros.
	@echo "🗨️  Testando chat via API com o modelo [$(MODEL)]..."
	@if [ -n "$(SYSTEM_PROMPT)" ]; then \
		echo "   (Usando prompt de sistema)"; \
		curl -s -X POST http://127.0.0.1:8000/chat \
		-H "Content-Type: application/json" \
		-d '{"model": "$(MODEL)", "messages": [{"role": "system", "content": "$(SYSTEM_PROMPT)"}, {"role": "user", "content": "$(PROMPT)"}], "params": {"temperature": $(TEMP), "max_tokens": $(MAX_TOKENS), "seed": 42}}'; \
	else \
		curl -s -X POST http://127.0.0.1:8000/chat \
		-H "Content-Type: application/json" \
		-d '{"model": "$(MODEL)", "messages": [{"role": "user", "content": "$(PROMPT)"}], "params": {"temperature": $(TEMP), "max_tokens": $(MAX_TOKENS), "seed": 42}}'; \
	fi

chat: ## Interage com o chat via CLI com todos os parâmetros.
	@echo "💬  Executando chat via CLI com o modelo [$(MODEL)]..."
	@$(DEV_COMPOSE) exec $(DEV_SERVICE_NAME) \
	python -m services.chat_service.app.cli.cli chat \
		--model "$(MODEL)" \
		--user "$(PROMPT)" \
		--temperature $(TEMP) \
		--max-tokens $(MAX_TOKENS) \
		$(if $(SYSTEM_PROMPT),--system "$(SYSTEM_PROMPT)")