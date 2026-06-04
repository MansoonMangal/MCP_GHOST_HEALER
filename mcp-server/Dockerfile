# Ghost Healer AI Brain — Production Dockerfile
FROM python:3.10-slim

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Set working directory to mcp-server root
# This ensures all relative imports (services/, ai_engine/, config/, utils/) resolve correctly
WORKDIR /app

# Install system dependencies needed by lxml
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    libxml2-dev \
    libxslt-dev \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Copy all mcp-server files into /app
COPY . .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Ensure database and log directories exist
RUN mkdir -p database reports/logs

# Set PYTHONPATH so app/main.py can import from sibling packages
ENV PYTHONPATH=/app

# Render injects PORT at runtime; entrypoint expands it (exec-form CMD does not)
RUN chmod +x /app/entrypoint.sh

EXPOSE 8000

CMD ["/app/entrypoint.sh"]
