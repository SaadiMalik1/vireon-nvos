# Multi-stage Dockerfile for VIREON Neurotechnology Validation OS v1.0.0
# Stage 1: Build & Dependency Installation Stage
FROM python:3.11-slim AS builder

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1

WORKDIR /build

RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    git \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --prefix=/install --no-cache-dir -r requirements.txt
RUN pip install --prefix=/install --no-cache-dir pytest hypothesis

# Stage 2: Final Production Stage
FROM python:3.11-slim AS runner

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    MPLBACKEND=Agg \
    PYTHONPATH=/install/lib/python3.11/site-packages:/app

WORKDIR /app

COPY --from=builder /install /install
COPY . /app/

CMD ["pytest", "--tb=no", "-q"]
