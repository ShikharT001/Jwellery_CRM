# ─────────────────────────────────────────────────────────────
# Jewellery ERP — FastAPI Backend Dockerfile
# ─────────────────────────────────────────────────────────────
# Multi-stage build:
#   Stage 1 (builder): Install dependencies
#   Stage 2 (runtime): Minimal production image

# ── Stage 1: Builder ──────────────────────────────────────────
FROM python:3.12-slim AS builder

WORKDIR /app

# Install system dependencies required for psycopg2
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Copy and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade pip \
    && pip install --no-cache-dir -r requirements.txt

# ── Stage 2: Runtime ──────────────────────────────────────────
FROM python:3.12-slim

WORKDIR /app

# Install runtime system dependencies only
RUN apt-get update && apt-get install -y --no-install-recommends \
    libpq5 \
    && rm -rf /var/lib/apt/lists/*

# Copy installed packages from builder
COPY --from=builder /usr/local/lib/python3.12/site-packages /usr/local/lib/python3.12/site-packages
COPY --from=builder /usr/local/bin /usr/local/bin

# Copy application code
COPY . .

# Create a non-root user for security
RUN useradd --no-create-home --shell /bin/false appuser
USER appuser

# Expose port
EXPOSE 8000

# Health check (matches our /health endpoint)
HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
    CMD python -c "import httpx; httpx.get('http://localhost:8000/health').raise_for_status()"

# Start command
# --workers: Number of uvicorn worker processes
# In production, use gunicorn with uvicorn workers for multi-process support
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "2"]
