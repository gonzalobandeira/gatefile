# Gatefile — Claude Context

## What this project does

Gatefile is a FastAPI service that acts as a proxy for S3 URLs. Clients register an S3 URL and receive a short-lived token-based proxy URL. When that URL is hit, the service streams the file directly from S3, forwarding range requests and relevant response headers.

## Architecture

- **FastAPI** app with two routes: `POST /register` and `GET /files/{token}`
- **Redis** for token → S3 URL storage (falls back to in-memory if `REDIS_URL` is not set)
- **nginx** as a reverse proxy and load balancer in front of 3 app replicas
- No auth on endpoints — tokens are the access control mechanism

## Key files

- `app/routes/register.py` — registers a URL, stores token in storage, returns proxy URL
- `app/routes/proxy.py` — resolves token, streams response from S3 with chunked transfer
- `app/storage.py` — `BaseStorage` interface with `RedisStorage` and `MemoryStorage` implementations
- `app/config.py` — settings via `pydantic-settings` (`BASE_URL`, `REDIS_URL`)
- `nginx/nginx.conf` — upstream block pointing to `app:8000`, round-robin across replicas
- `docker-compose.yml` — redis + 3 app replicas + nginx

## Running

```bash
docker compose up --build
```

## Conventions

- Async throughout (`httpx.AsyncClient`, `aioredis`)
- Storage operations: `get`, `set`, `delete`, `close`
- Proxy streams in 64KB chunks, never buffers full file in memory
- On S3 4xx, the token is deleted from storage automatically
