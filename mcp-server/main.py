"""
DEPRECATED: Flask entrypoint replaced by FastAPI + MCP.

Use instead:
  uvicorn app.main:app --host 0.0.0.0 --port 8000

Or production Docker CMD (gunicorn app.main:app).
"""
import warnings

warnings.warn(
    "mcp-server/main.py (Flask) is deprecated. Use app.main:app (FastAPI + MCP).",
    DeprecationWarning,
    stacklevel=1,
)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=False)
