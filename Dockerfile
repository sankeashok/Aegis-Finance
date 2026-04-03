# ─────────────────────────────────────────────────────────────────────────────
# Project Aegis-Finance: Production Dockerfile
# Stage 1: Builder — installs only runtime dependencies
# Stage 2: Runtime — minimal image, non-root user, no dev tools
# ─────────────────────────────────────────────────────────────────────────────

# ── Stage 1: Dependency Builder ───────────────────────────────────────────────
FROM python:3.11-slim AS builder

WORKDIR /build

# Copy and install runtime deps only (no pip cache to reduce image size)
COPY requirements.txt .

# Strip dev/notebook packages for leaner image
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

# ── Stage 2: Production Runtime ───────────────────────────────────────────────
FROM python:3.11-slim AS runtime

LABEL maintainer="Project-Aegis-Finance"
LABEL version="1.0.0"
LABEL description="Aegis Risk Gateway – Production API"

# Security: Run as a non-root user
RUN groupadd -r appgroup && useradd -r -g appgroup appuser

WORKDIR /aegis

# Copy installed packages from builder
COPY --from=builder /usr/local/lib/python3.11/site-packages /usr/local/lib/python3.11/site-packages
COPY --from=builder /usr/local/bin/uvicorn /usr/local/bin/uvicorn

# Copy application source only (not .venv, data, notebooks, _temp)
COPY app/ ./app/
COPY models/ ./models/

# Set ownership
RUN chown -R appuser:appgroup /aegis

USER appuser

EXPOSE 8000

# Health check: ping the root endpoint every 30s
HEALTHCHECK --interval=30s --timeout=5s --start-period=10s --retries=3 \
    CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:8000/')" || exit 1

# Start the Risk Gateway
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "2"]
