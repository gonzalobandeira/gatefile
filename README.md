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

## Environment variables

| Variable    | Description                        | Default               |
|-------------|------------------------------------|-----------------------|
| `BASE_URL`  | Public base URL for proxy links    | `http://localhost`    |
| `REDIS_URL` | Redis connection URL               | in-memory if not set  |
