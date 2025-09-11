# 🐳 Docker — Chat Service (FastAPI + CLI)

Este diretório contém o `Dockerfile` e instruções para rodar a aplicação **Chat Service** (API + CLI) usando Docker.

> **Contexto do projeto**
> - API FastAPI com entrypoint: `services.chat_service.app.api.main:app`
> - Porta interna padrão: **8000**
> - Endpoints: `/healthz`, `/models`, `/chat`
> - CLI: `python -m services.chat_service.app.cli.cli`
> - Arquivo `.env.example` na raiz (crie o seu `.env` **fora do Git**)

---

## 📚 Sumário

- Estrutura do projeto
- Pré-requisitos
- [TL;DR (execução rápida)](#tldr-execuçãoem](#-build-da-imagem)
- [Executar o container](#-executar-o-container)
- Testar a API
- [Executar a CLI](#-executs de ambiente (.env)
- Persistência (volumes) e permissões
- Boas práticas
- Troubleshooting
- Limpeza
- Build multi‑arch (opcional)
-/ Pessoa 2)

---

## 📂 Estrutura do projeto

