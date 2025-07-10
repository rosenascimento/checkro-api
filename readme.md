# Checkro API (FastAPI + Celery + PostgreSQL)

API para análise automatizada de conteúdo em sites e blogs, com base nas políticas do Google AdSense.

## Rodando localmente

### Linux/macOS

```bash
cp .env.example .env
docker-compose up --build
```

### Windows (Prompt de Comando)

```cmd
copy .env.example .env
docker-compose up --build
```

## Endpoints disponíveis

- Swagger UI: [http://localhost:8000/docs](http://localhost:8000/docs)  
- ReDoc: [http://localhost:8000/redoc](http://localhost:8000/redoc)

## Variáveis de ambiente

Exemplo de `.env`:

```env
DATABASE_URL=postgresql://usuario:senha@db:5432/checkro
REDIS_URL=redis://redis:6379/0
```

## Estrutura do projeto

```
.
├── app/
│   ├── models/
│   ├── tasks/
│   ├── api/
│   └── main.py
├── Dockerfile
├── docker-compose.yml
├── .env.example
├── README.md
```

## Rodando Celery manualmente

Caso queira rodar o worker Celery manualmente:

```bash
celery -A app.tasks.worker worker --loglevel=info
```

## Deploy na Azure

1. Faça o build da imagem:

```bash
docker build -t checkro-api .
```

2. Envie a imagem para seu Container Registry (ACR ou Docker Hub):

```bash
docker tag checkro-api <seu-registro>.azurecr.io/checkro-api
docker push <seu-registro>.azurecr.io/checkro-api
```

3. Crie um **Web App for Containers** no Azure e configure:

- Porta: `8000`
- Variáveis de ambiente: `DATABASE_URL`, `REDIS_URL`, etc.

4. Para o Celery, use um container separado (Azure Container Apps, WebJob ou outro serviço).

---

Desenvolvido com ❤️ para escalar projetos com qualidade de conteúdo.
