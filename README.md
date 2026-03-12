# Gatefile

A lightweight file proxy service. Register an S3 URL and get back a token-based proxy URL that streams the file through the service.

## How it works

1. `POST /register` with an S3 URL → returns a proxy URL with a token
2. `GET /files/{token}` → streams the file from S3, forwarding range requests and relevant headers

## Running locally

```bash
cp .env.example .env
docker compose up --build
```

The service will be available at `http://localhost` (nginx → 3 app replicas → Redis).

## API

### Register a URL

```bash
curl -X POST http://localhost/register \
  -H "Content-Type: application/json" \
  -d '{"url": "https://your-bucket.s3.amazonaws.com/file.pdf"}'
```

Response:
```json
{"proxy_url": "http://localhost/files/<token>"}
```

### Download via proxy

```bash
curl http://localhost/files/<token> -o file.pdf
```

Supports `Range` requests for partial content.

## Horizontal scaling

Gatefile is designed to scale horizontally. Multiple app instances can run concurrently because all shared state (token → S3 URL mappings) lives in Redis, not in local memory.

```
clients → nginx (round-robin) → app replica 1 ─┐
                               → app replica 2 ─┼→ Redis
                               → app replica 3 ─┘
```

A token registered on replica 1 can be resolved by replica 2 or 3 on the next request — any instance can serve any token. Without Redis, each replica would have its own isolated in-memory store, causing frequent 404s depending on which instance handled the request.

To scale up or down:

```bash
docker compose up --scale app=5
```

The default `docker-compose.yml` starts 3 replicas. For production, point `REDIS_URL` at a managed Redis instance (e.g. ElastiCache, Redis Cloud) and run as many app containers as needed behind a load balancer.

## Environment variables

| Variable    | Description                        | Default               |
|-------------|------------------------------------|-----------------------|
| `BASE_URL`  | Public base URL for proxy links    | `http://localhost`    |
| `REDIS_URL` | Redis connection URL               | in-memory if not set  |
