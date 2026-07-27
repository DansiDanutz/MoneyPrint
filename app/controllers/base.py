from uuid import uuid4

from fastapi import Request, Security
from fastapi.security import APIKeyHeader

from app.config import config
from app.models.exception import HttpException


api_key_header = APIKeyHeader(
    name="x-api-key",
    scheme_name="ApiKeyAuth",
    auto_error=False,
)


def get_task_id(request: Request):
    task_id = request.headers.get("x-task-id")
    if not task_id:
        task_id = uuid4()
    return str(task_id)


def get_api_key(request: Request):
    api_key = request.headers.get("x-api-key")
    return api_key


def verify_token(request: Request, token: str | None = Security(api_key_header)):
    request_id = get_task_id(request)
    configured_token = config.app.get("api_key", "")
    if not configured_token:
        raise HttpException(
            task_id=request_id,
            status_code=503,
            message=f"{request_id}: API authentication is not configured",
        )
    if token != configured_token:
        raise HttpException(
            task_id=request_id,
            status_code=401,
            message=f"{request_id}: invalid token",
        )
