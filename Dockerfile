# Demo de Ensayo (FastAPI + web/). Escucha en 8040; /health para el health check.
FROM python:3.12-slim AS build
COPY --from=ghcr.io/astral-sh/uv:0.8.17 /uv /bin/uv
WORKDIR /app
ENV UV_COMPILE_BYTECODE=1 UV_LINK_MODE=copy
COPY pyproject.toml uv.lock ./
RUN uv sync --frozen --no-dev --no-install-project
COPY ensayo ./ensayo
RUN uv sync --frozen --no-dev

FROM python:3.12-slim
WORKDIR /app
RUN useradd --create-home --uid 1000 ensayo
COPY --from=build /app/.venv /app/.venv
COPY ensayo ./ensayo
COPY web ./web
RUN mkdir -p results && chown ensayo results
USER ensayo
ENV PATH="/app/.venv/bin:$PATH" PYTHONUNBUFFERED=1
EXPOSE 8040
CMD ["uvicorn", "ensayo.api:app", "--host", "0.0.0.0", "--port", "8040", "--proxy-headers", "--forwarded-allow-ips", "*"]
