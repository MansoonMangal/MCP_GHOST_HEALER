"""
API key authentication for REST and MCP HTTP surfaces.
"""
from typing import Optional

from fastapi import HTTPException, Request
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import JSONResponse

from config.settings import settings


PUBLIC_PATHS = frozenset({
    "/health",
    "/api/health",
    "/docs",
    "/openapi.json",
    "/redoc",
})


def _is_public(path: str) -> bool:
    if path in PUBLIC_PATHS:
        return True
    if path.startswith("/docs") or path.startswith("/redoc"):
        return True
    return False


def verify_api_key(request: Request) -> Optional[str]:
    """Return API key if valid; None if auth disabled."""
    if not settings.api_key:
        return None

    provided = (
        request.headers.get("X-API-Key")
        or request.headers.get("Authorization", "").replace("Bearer ", "").strip()
    )
    if not provided or provided != settings.api_key:
        raise HTTPException(status_code=401, detail="Invalid or missing API key")
    return provided


class APIKeyMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        path = request.url.path
        if _is_public(path):
            return await call_next(request)

        if settings.api_key:
            try:
                verify_api_key(request)
            except HTTPException as exc:
                return JSONResponse(
                    status_code=exc.status_code,
                    content={"detail": exc.detail},
                )

        return await call_next(request)
