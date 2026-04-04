# ─────────────────────────────────────────────────────────────────────────────
# Project Aegis-Finance: Unified Production Dockerfile
# Stage 1: Frontend Builder — Compiles React UI
# Stage 2: Backend Builder — Installs Python dependencies
# Stage 3: Unified Runtime — Minimal image, serving both UI and API
# ─────────────────────────────────────────────────────────────────────────────

# ── Stage 1: Frontend Builder ────────────────────────────────────────────────
FROM node:20-slim AS frontend-builder
WORKDIR /frontend
COPY frontend/package*.json ./
RUN npm install
COPY frontend/ .
RUN npm run build

# ── Stage 2: Backend Builder ─────────────────────────────────────────────────
FROM python:3.11-slim AS python-builder
WORKDIR /build

# Install build dependencies if needed (e.g., for compiled deps)
# apt-get update && apt-get install -y build-essential for any compiled packages
COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade pip \
    && pip install --no-cache-dir -r requirements.txt

# ── Stage 3: Unified Production Runtime ──────────────────────────────────────
FROM python:3.11-slim AS runtime
LABEL maintainer="Project-Aegis-Finance"
LABEL version="1.3.0"

# Install runtime dependencies (e.g., libgomp1 for XGBoost)
RUN apt-get update && apt-get install -y --no-install-recommends \
    libgomp1 \
    && rm -rf /var/lib/apt/lists/*

# Security: Run as a non-root user
RUN groupadd -r appgroup && useradd -r -g appgroup appuser
WORKDIR /aegis

# Copy Python packages from builder
COPY --from=python-builder /usr/local/lib/python3.11/site-packages /usr/local/lib/python3.11/site-packages
COPY --from=python-builder /usr/local/bin/uvicorn /usr/local/bin/uvicorn

# Copy Frontend dist from builder
COPY --from=frontend-builder /frontend/dist ./frontend/dist

# Copy application source and models
COPY app/ ./app/
COPY models/ ./models/

# Set ownership
RUN chown -R appuser:appgroup /aegis
USER appuser
EXPOSE 8000

# Health check (Ensure app is up)
HEALTHCHECK --interval=30s --timeout=5s --start-period=10s --retries=3 \
    CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:8000/health')" || exit 1

# Start Gateway
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "2"]
