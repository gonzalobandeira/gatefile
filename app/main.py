from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.config import settings
from app.routes.proxy import router as proxy_router
from app.routes.register import router as register_router
from app.storage import MemoryStorage, RedisStorage


@asynccontextmanager
async def lifespan(app: FastAPI):
    if settings.redis_url:
        storage = RedisStorage(settings.redis_url)
    else:
        storage = MemoryStorage()

    app.state.storage = storage
    yield
    await storage.close()


app = FastAPI(title="Gatefile", lifespan=lifespan)

app.include_router(register_router)
app.include_router(proxy_router)


@app.get("/health")
async def health():
    return {"status": "ok"}
