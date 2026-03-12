from fastapi import Request

from app.storage import BaseStorage


def get_storage(request: Request) -> BaseStorage:
    return request.app.state.storage
