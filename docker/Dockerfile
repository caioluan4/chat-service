# syntax=docker/dockerfile:1.7
FROM python:3.12-slim AS base

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    PORT=8000

WORKDIR /app

# Cria usuário não-root ANTES do COPY para poder usar --chown
RUN useradd -m appuser

# Dependências
COPY ../requirements.txt .
RUN --mount=type=cache,target=/root/.cache/pip \
    pip install --upgrade pip && pip install -r requirements.txt

# Copia o código já com o dono correto
COPY --chown=appuser:appuser . .

# (Opcional) garantir que 'runs' exista, caso seu repo não tenha a pasta
RUN mkdir -p services/chat_service/runs

USER appuser

EXPOSE 8000

HEALTHCHECK --interval=30s --timeout=5s --retries=3 \
  CMD python -c "import urllib.request; urllib.request.urlopen('http://127.0.0.1:8000/healthz', timeout=3)"

CMD ["python", "-m", "uvicorn", "services.chat_service.app.api.main:app", "--host", "0.0.0.0", "--port", "8000"]
