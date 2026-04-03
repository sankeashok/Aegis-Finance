# ─────────────────────────────────────────────────────────────────────────────
# Project Aegis-Finance: Unified Production Dockerfile
# Stage 1: Frontend Builder — Compiles React UI
# Stage 2: Backend Builder — Installs Python dependencies
# Stage 3: Unified Runtime — Minimal image, serving both UI and API
# ─────────────────────────────────────────────────────────────────────────────

# ── Stage 1: Frontend Builder ────────────────────────────────────────────────
FROM node:20-slim AS frontend-builder

WORKDIR /frontend

# Install dependencies (leverage Docker cache)
COPY frontend/package*.json ./
RUN npm install

# Copy source and build (ensure vite.config.js and public/ are included)
COPY frontend/ .
RUN npm run build

# ── Stage 2: Backend Builder ─────────────────────────────────────────────────
FROM python:3.11-slim AS python-builder

WORKDIR /build

COPY requirements.txt .

RUN pip install --no-cache-dir --upgrade pip \
    && pip install --no-cache-dir \
        fastapi==0.115.6 \
        "uvicorn[standard]==0.34.0" \
        pandas==2.2.3 \
        pyarrow==19.0.1 \
        scikit-learn==1.6.1 \
        xgboost==2.1.4 \
        joblib \
        httpx==0.28.1 \
        prometheus-fastapi-instrumentator==7.0.0

# ── Stage 3: Unified Production Runtime ──────────────────────────────────────
FROM python:3.11-slim AS runtime

LABEL maintainer="Project-Aegis-Finance"
LABEL version="1.1.0"
LABEL description="Aegis Risk Gateway – Unified UI & API"

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

# Set ownership for security
RUN chown -R appuser:appgroup /aegis

USER appuser

EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=5s --start-period=10s --retries=3 \
    CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:8000/')" || exit 1

# Start the Gateway (unified UI + API)
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "2"]
