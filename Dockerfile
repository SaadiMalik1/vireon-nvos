FROM python:3.11-slim AS builder

WORKDIR /build
COPY pyproject.toml requirements.txt ./
COPY vireon-core ./vireon-core
COPY vireon-methods ./vireon-methods
COPY vireon-validation ./vireon-validation
COPY vireon-evidence ./vireon-evidence
COPY vireon-corpus ./vireon-corpus
COPY vireon-knowledge ./vireon-knowledge
COPY vireon-models ./vireon-models
COPY vireon-lab ./vireon-lab
COPY vireon-api ./vireon-api
COPY vireon-verification ./vireon-verification

RUN pip install --no-cache-dir -e ".[api]"

# --- Runtime stage ---
FROM python:3.11-slim

WORKDIR /app
COPY --from=builder /usr/local/lib/python3.11/site-packages /usr/local/lib/python3.11/site-packages
COPY --from=builder /build /app

# Create non-root user
RUN useradd -m -u 1000 vireon && chown -R vireon:vireon /app
USER vireon

EXPOSE 8000

HEALTHCHECK --interval=30s --timeout=5s --start-period=10s --retries=3 \
    CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:8000/api/health').read()"

CMD ["uvicorn", "vireon_api.main:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "4"]
