FROM python:3.12-slim

WORKDIR /app

# Install uv
COPY --from=ghcr.io/astral-sh/uv:latest /uv /usr/local/bin/uv

ENV UV_COMPILE_BYTECODE=1 \
    UV_LINK_MODE=copy \
    UV_PYTHON_DOWNLOADS=never \
    PYTHONPATH=/app/Backend

# Copy dependency files
COPY pyproject.toml uv.lock ./

# Install production dependencies
RUN uv sync --frozen --no-dev

# Copy backend
COPY Backend ./Backend

# Copy trained models
COPY ["ML/ML models", "ML/ML models"]

EXPOSE 8000

CMD ["uv", "run", "uvicorn", "app.main:app", "--app-dir", "/app/Backend", "--host", "0.0.0.0", "--port", "8000"]