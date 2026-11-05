# syntax=docker/dockerfile:1

# ---------- frontend ----------
FROM node:22-alpine AS web
WORKDIR /web
COPY web/package.json web/package-lock.json ./
RUN npm ci --no-audit --no-fund
COPY web/ ./
RUN npm run build

# ---------- backend ----------
FROM python:3.12-slim AS app
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1 \
    DATA_DIR=/data \
    STATIC_DIR=/app/static \
    PORT=8000
WORKDIR /app

COPY src/bsdd_json /app/src/bsdd_json
COPY src/bsdd_web /app/src/bsdd_web
RUN pip install /app/src/bsdd_json /app/src/bsdd_web && rm -rf /app/src

COPY --from=web /web/dist /app/static

RUN useradd --system --uid 1000 --create-home bsdd \
    && mkdir -p /data && chown bsdd:bsdd /data
USER bsdd
VOLUME /data
EXPOSE 8000

HEALTHCHECK --interval=30s --timeout=5s --start-period=20s --retries=3 \
  CMD python -c "import os,urllib.request; urllib.request.urlopen(f'http://127.0.0.1:{os.environ.get(\"PORT\",\"8000\")}/api/health', timeout=4)"

# A single worker is required: open dictionaries are kept in memory.
CMD ["bsdd-web"]
