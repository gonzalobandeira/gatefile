import uuid

from fastapi import APIRouter, Depends
from pydantic import BaseModel

from app.config import settings
from app.dependencies import get_storage
from app.storage import BaseStorage

router = APIRouter()


class RegisterRequest(BaseModel):
    url: str


class RegisterResponse(BaseModel):
    proxy_url: str


@router.post("/register", response_model=RegisterResponse)
async def register(
    body: RegisterRequest,
    storage: BaseStorage = Depends(get_storage),
) -> RegisterResponse:
    token = str(uuid.uuid4())
    await storage.set(token, body.url)
    return RegisterResponse(proxy_url=f"{settings.base_url}/files/{token}")
