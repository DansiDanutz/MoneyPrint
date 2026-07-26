from uuid import uuid4

from fastapi import Request

from app.config import config
from app.models.exception import HttpException


def get_task_id(request: Request):
    task_id = request.headers.get("x-task-id")
    if not task_id:
        task_id = uuid4()
    return str(task_id)


def get_api_key(request: Request):
    api_key = request.headers.get("x-api-key")
    return api_key


def verify_token(request: Request):
    request_id = get_task_id(request)
    configured_token = config.app.get("api_key", "")
    if not configured_token:
        raise HttpException(
            task_id=request_id,
            status_code=503,
            message=f"{request_id}: API authentication is not configured",
        )
    token = get_api_key(request)
    if token != configured_token:
        raise HttpException(
            task_id=request_id,
            status_code=401,
            message=f"{request_id}: invalid token",
        )
