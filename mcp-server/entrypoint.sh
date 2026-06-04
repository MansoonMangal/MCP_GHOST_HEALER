#!/bin/sh
set -e
PORT="${PORT:-8000}"
WORKERS="${WEB_CONCURRENCY:-1}"
exec gunicorn app.main:app \
  --worker-class uvicorn.workers.UvicornWorker \
  --workers "${WORKERS}" \
  --bind "0.0.0.0:${PORT}" \
  --timeout 120 \
  --keep-alive 5 \
  --log-level info
