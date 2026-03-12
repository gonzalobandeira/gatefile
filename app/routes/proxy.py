import httpx
from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi.responses import StreamingResponse

from app.dependencies import get_storage
from app.storage import BaseStorage

router = APIRouter()

# Headers from S3 that are meaningful to forward to the client
FORWARDED_HEADERS = {
    "content-type",
    "content-length",
    "content-range",
    "content-disposition",
    "accept-ranges",
    "etag",
    "last-modified",
}


@router.get("/files/{token}")
async def proxy(
    token: str,
    request: Request,
    storage: BaseStorage = Depends(get_storage),
) -> StreamingResponse:
    s3_url = await storage.get(token)
    if s3_url is None:
        raise HTTPException(status_code=404, detail="Not found")

    upstream_headers = {}
    if range_header := request.headers.get("range"):
        upstream_headers["range"] = range_header

    # Create client with no timeout — files can be large and slow to transfer
    client = httpx.AsyncClient(timeout=None)
    s3_request = client.build_request("GET", s3_url, headers=upstream_headers)

    try:
        s3_response = await client.send(s3_request, stream=True)
    except httpx.RequestError:
        await client.aclose()
        raise HTTPException(status_code=502, detail="Failed to reach S3")

    if s3_response.status_code >= 400:
        await s3_response.aclose()
        await client.aclose()
        await storage.delete(token)
        raise HTTPException(status_code=410, detail="URL expired or no longer available")

    response_headers = {
        k: v
        for k, v in s3_response.headers.items()
        if k.lower() in FORWARDED_HEADERS
    }

    async def generate():
        try:
            async for chunk in s3_response.aiter_bytes(chunk_size=65536):
                yield chunk
        finally:
            await s3_response.aclose()
            await client.aclose()

    return StreamingResponse(
        generate(),
        status_code=s3_response.status_code,
        headers=response_headers,
    )
