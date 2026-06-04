"""Request payload size limits for DOM snapshots."""
from fastapi import HTTPException, Request
from starlette.middleware.base import BaseHTTPMiddleware

from config.settings import settings


class PayloadLimitMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        if request.method in ("POST", "PUT", "PATCH"):
            content_length = request.headers.get("content-length")
            if content_length:
                try:
                    size = int(content_length)
                except ValueError:
                    size = 0
                if size > settings.max_request_bytes:
                    raise HTTPException(
                        status_code=413,
                        detail=f"Payload too large. Max {settings.max_request_bytes} bytes.",
                    )
        return await call_next(request)
