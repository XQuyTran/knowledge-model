# Local Diagnostic Web App

This update adds:

- `POST /diagnose` FastAPI endpoint
- simple web frontend at `/`
- Dockerfile for the Python app
- docker-compose configuration that loads `.env` and `.env.llm`

## Run locally

```bash
cp .env.example .env
cp .env.llm.example .env.llm
# edit .env.llm and set your real LLM key

docker compose up -d --build neo4j app
```

Open:

- App UI: http://localhost:8000
- API docs: http://localhost:8000/docs
- Health: http://localhost:8000/health
- Neo4j Browser: http://localhost:7474

## Load Neo4j seed files

Place the generated `.cypher` seed files beside `docker-compose.yml`, then run:

```bash
docker compose --profile seed up --abort-on-container-exit neo4j-seed
```
