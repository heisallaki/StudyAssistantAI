FROM python:3.12-slim AS builder

WORKDIR /build

RUN apt-get update \
    && apt-get install -y --no-install-recommends build-essential \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .

RUN python -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

RUN pip install --no-cache-dir --upgrade pip \
    && pip install --no-cache-dir -r requirements.txt

ENV EMBEDDING_CACHE_DIR=/app/.fastembed_cache

RUN python -c "from fastembed import TextEmbedding; TextEmbedding(model_name='sentence-transformers/all-MiniLM-L6-v2', cache_dir='/app/.fastembed_cache')"


FROM python:3.12-slim AS runtime

RUN groupadd --system app && useradd --system --gid app --home-dir /app app

WORKDIR /app

COPY --from=builder /opt/venv /opt/venv
COPY --from=builder /app/.fastembed_cache /app/.fastembed_cache
COPY alembic ./alembic
COPY alembic.ini .
COPY app ./app

ENV PATH="/opt/venv/bin:$PATH" \
    PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    EMBEDDING_CACHE_DIR=/app/.fastembed_cache \
    PORT=8000

RUN chown -R app:app /app

USER app

EXPOSE 8000

CMD alembic upgrade head && uvicorn app.main:app --host 0.0.0.0 --port ${PORT}