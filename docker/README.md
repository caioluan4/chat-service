# Chat Service (FastAPI) - Dockerizado

Este projeto fornece uma configuração Docker para o **Chat Service**, uma aplicação Python construída com FastAPI.

Este guia contém tudo o que você precisa para construir a imagem Docker, executar o contêiner e testar a aplicação usando tanto o Docker quanto o Docker Compose. A configuração inclui ambientes distintos para **desenvolvimento** (com hot-reload) e **produção**.

## Contexto do Projeto

* **Framework da API**: FastAPI
* **Ponto de Entrada (Entrypoint)**: `services.chat_service.app.api.main:app`
* **Porta Padrão**: `8088`
* **Endpoints Principais**:
    * `/healthz`: Verificação de saúde (health check)
    * `/models`: Visualização dos modelos configurados
    * `/chat`: Funcionalidade principal de chat
* **Interface de Linha de Comando (CLI)**: `python -m services.chat_service.app.cli.cli`

---

## ✅ Pré-requisitos

Antes de começar, certifique-se de que você tem os seguintes itens instalados e configurados:

* **Docker & Docker Compose**:
    * Docker versão 24.0 ou superior.
    * Docker Compose v2.0 ou superior.
* **Arquivo de Ambiente**:
    * Crie um arquivo `.env` no diretório raiz do projeto, copiando o arquivo `.env.example`. Este arquivo deve conter todas as variáveis de ambiente necessárias, mas **não** deve ser enviado para o Git.
* **Arquivos de Configuração**:
    * Garanta que você tenha um arquivo `models.json` localizado em `services/chat_service/config/`.
* **Dependências Python**:
    * Um arquivo `requirements.txt` é necessário (na raiz). Um exemplo mínimo é:
        ```txt
        fastapi
        uvicorn[standard]
        litellm
        python-dotenv
        ```

---

## 🚀 Como Começar

Você pode executar a aplicação usando um contêiner Docker avulso ou com Docker Compose para uma orquestração mais avançada (recomendado).

### Opção 1: Usando `docker run` (Método Simples)

Este método é ideal para um teste rápido e isolado da aplicação.

1.  **Construa a Imagem Docker (Build)**
    Execute o comando a seguir na raiz do projeto para construir a imagem:
    ```bash
    docker build -t chat-service:local .
    ```

2.  **Execute o Contêiner**
    Quando a construção estiver finalizada, execute o contêiner. Este comando mapeia a porta 8000 da sua máquina local para a porta 8088 dentro do contêiner e carrega as variáveis de ambiente do seu arquivo `.env`.
    ```bash
    docker run --rm -p 8088:8000 --env-file .env chat-service:local
    ```
    > **Nota**: Se a porta 8088 já estiver em uso na sua máquina, você pode mapeá-la para uma porta diferente (ex: `8088:8000`).

3.  **Valide a Aplicação**
    * **Health Check da API**: Abra um novo terminal e use o `curl` para verificar se a API está em execução:
        ```bash
        curl http://127.0.0.1:8088/healthz
        ```
        Você deve receber uma resposta `200 OK`.

    * **Teste a CLI**: Para testar a interface de linha de comando, encontre o ID do seu contêiner e execute o comando da CLI dentro dele.
        ```bash
        # Encontre o ID do contêiner
        docker ps

        # Execute o comando da CLI (substitua <CONTAINER_ID> pelo ID real)
        docker exec -it <CONTAINER_ID> python -m services.chat_service.app.cli.cli models
        ```

### Opção 2: Usando Docker Compose (Recomendado)

O Docker Compose simplifica o gerenciamento da aplicação, especialmente com diferentes ambientes como desenvolvimento e produção.

#### Ambiente de Desenvolvimento (com Hot-Reload)

Este perfil é configurado para o desenvolvimento ativo. Ele monta seu código local dentro do contêiner, e o servidor reiniciará automaticamente quando você fizer alterações no código.

1.  **Inicie o Serviço**
    Use o perfil `dev` para construir e iniciar o contêiner em modo "detached" (em segundo plano):
    ```bash
    docker compose --profile dev up -d
    ```

2.  **Valide e Interaja**
    * **Verifique os Logs**: Para visualizar os logs da aplicação em tempo real:
        ```bash
        docker compose --profile dev logs -f chat-service
        ```
    * **Health Check da API**:
        ```bash
        curl http://127.0.0.1:8088/healthz
        ```
    * **Execute Comandos da CLI**:
        ```bash
        docker compose --profile dev exec chat-service \
          python -m services.chat_service.app.cli.cli models
        ```

#### Ambiente de Produção

Este perfil utiliza uma imagem imutável, sem montagem de código ou hot-reloading, simulando um ambiente de produção.

1.  **Inicie o Serviço**
    Use o perfil `prod` para construir e iniciar o contêiner:
    ```bash
    docker compose --profile prod up -d
    ```

2.  **Valide**
    * **Verifique os Logs**:
        ```bash
        docker compose --profile prod logs -f chat-service-prod
        ```
    * **Health Check da API**:
        ```bash
        curl http://127.0.0.1:8088/healthz
        ```

---

## 🛠️ Funcionalidades e Boas Práticas

Esta configuração Docker foi construída com os seguintes princípios em mente:

* **Segurança**: O contêiner é executado com um usuário não-root (`appuser`) para reduzir riscos de segurança.
* **Eficiência**: Utiliza uma imagem base leve (`python:3.12-slim`) e um arquivo `.dockerignore` para manter o tamanho da imagem mínimo. O cache de build para o `pip` está ativado para construções mais rápidas.
* **Reprodutibilidade**: As versões do Python e das dependências devem ser fixadas para garantir builds consistentes.
* **Observabilidade**: Um `HEALTHCHECK` está incluído no `Dockerfile` e o endpoint `/healthz` está disponível para monitoramento. O diretório `runs/` é montado como um volume para persistir telemetria e métricas.
* **Gerenciamento de Configuração**: O diretório `config/` é montado como um volume somente leitura para prevenir modificações acidentais em tempo de execução. As variáveis de ambiente são gerenciadas de forma centralizada via `.env` e `env_file` no Docker Compose.
* **Experiência de Desenvolvimento**: O perfil `dev` no Docker Compose habilita o hot-reloading para um fluxo de trabalho de desenvolvimento mais ágil.

---

## ⚙️ Referência de Comandos

Aqui está uma referência rápida para os comandos mais comuns:

| Descrição                         | Comando                                                               |
| ----------------------------------- | --------------------------------------------------------------------- |
| **Docker Avulso** |                                                                       |
| Construir Imagem                    | `docker build -t chat-service:local .`                                |
| Executar Contêiner                  | `docker run --rm -p 8000:8000 --env-file .env chat-service:local`      |
| **Docker Compose (Desenvolvimento)**|                                                                       |
| Iniciar Serviços                    | `docker compose --profile dev up -d`                                  |
| Ver Logs                            | `docker compose --profile dev logs -f chat-service`                   |
| Executar CLI                        | `docker compose --profile dev exec chat-service <COMANDO>`            |
| Parar Serviços                      | `docker compose --profile dev down`                                   |
| **Docker Compose (Produção)** |                                                                       |
| Iniciar Serviços                    | `docker compose --profile prod up -d`                                 |
| Ver Logs                            | `docker compose --profile prod logs -f chat-service-prod`             |
| Parar Serviços                      | `docker compose --profile prod down`                                  |
| **Testes da API** |                                                                       |
| Health Check                        | `curl http://127.0.0.1:8000/healthz`                                  |
| Listar Modelos                      | `curl http://127.0.0.1:8000/models`                                   |

---

## Troubleshooting (Solução de Problemas)

* **"Port is already occupied" (Porta já está em uso)**: Mude o mapeamento de porta no comando `docker run` ou no arquivo `docker-compose.yml`. Por exemplo, altere `-p 8000:8000` para `-p 8080:8000`.
* **Healthcheck falha ou a aplicação não inicia**:
    1.  Verifique se o seu arquivo `.env` está completo e correto.
    2.  Garanta que o arquivo `models.json` existe em `services/chat_service/config/`.
    3.  Verifique os logs do contêiner para mensagens de erro específicas.
* **Erros de permissão no diretório `runs/`**: Se encontrar problemas de permissão, crie o diretório na sua máquina local antes de iniciar o contêiner: `mkdir -p services/chat_service/runs`.