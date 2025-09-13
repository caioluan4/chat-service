# syntax=docker/dockerfile:1.7

# --- Estágio Base ---
FROM python:3.12-slim AS base

# Define variáveis de ambiente globais
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    # Define o local do cache para o Hugging Face, dentro do home do usuário
    HF_HOME=/home/appuser/.cache/huggingface \
    PORT=8000

# Cria um usuário não-root para segurança
# O diretório home /home/appuser será criado automaticamente
RUN useradd -ms /bin/bash appuser

# Define o diretório de trabalho principal
WORKDIR /app

# --- Estágio de Dependências ---
FROM base AS builder

# Copia apenas o necessário para instalar as dependências
COPY requirements.txt .

# Instala as dependências usando cache do Docker para acelerar builds futuros
RUN --mount=type=cache,target=/root/.cache/pip \
    pip install --upgrade pip && pip install -r requirements.txt

# --- Estágio Final da Aplicação ---
FROM base AS app

# Copia as dependências já instaladas do estágio anterior
COPY --from=builder /usr/local/lib/python3.12/site-packages /usr/local/lib/python3.12/site-packages

# Copia todo o código do projeto para o diretório de trabalho /app
# O contexto do build é a raiz do projeto (definido no docker-compose.yml)
COPY . .

# Define o WORKDIR para a raiz da aplicação Python
WORKDIR /app/services/chat_service

# Define o usuário 'appuser' como dono de todos os arquivos do app e do seu diretório home (para o cache)
# Isso é feito como root ANTES de mudar o usuário final
RUN chown -R appuser:appuser /app /home/appuser

# Muda para o usuário não-root
USER appuser

# Expõe a porta que a aplicação vai usar
EXPOSE 8000

# Define o Health Check
HEALTHCHECK --interval=30s --timeout=5s --retries=3 \
  CMD python -c "import urllib.request; urllib.request.urlopen('http://127.0.0.1:8000/healthz', timeout=3)"

# Comando final para iniciar a aplicação, agora com o caminho correto
CMD ["python", "-m", "uvicorn", "app.api.main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]