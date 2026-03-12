from abc import ABC, abstractmethod
from typing import Optional

import redis.asyncio as aioredis


class BaseStorage(ABC):
    @abstractmethod
    async def set(self, token: str, url: str) -> None:
        pass

    @abstractmethod
    async def get(self, token: str) -> Optional[str]:
        pass

    @abstractmethod
    async def delete(self, token: str) -> None:
        pass

    async def close(self) -> None:
        """Optional teardown — override in backends that hold connections."""
        pass


class MemoryStorage(BaseStorage):
    def __init__(self) -> None:
        self._store: dict[str, str] = {}

    async def set(self, token: str, url: str) -> None:
        self._store[token] = url

    async def get(self, token: str) -> Optional[str]:
        return self._store.get(token)

    async def delete(self, token: str) -> None:
        self._store.pop(token, None)


class RedisStorage(BaseStorage):
    def __init__(self, redis_url: str) -> None:
        self._client: aioredis.Redis = aioredis.from_url(
            redis_url, decode_responses=True
        )

    async def set(self, token: str, url: str) -> None:
        await self._client.set(token, url)

    async def get(self, token: str) -> Optional[str]:
        return await self._client.get(token)

    async def delete(self, token: str) -> None:
        await self._client.delete(token)

    async def close(self) -> None:
        await self._client.aclose()
