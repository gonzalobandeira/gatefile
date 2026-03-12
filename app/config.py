from typing import Optional

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    base_url: str = "http://localhost:8000"
    redis_url: Optional[str] = None

    model_config = {"env_file": ".env"}


settings = Settings()
