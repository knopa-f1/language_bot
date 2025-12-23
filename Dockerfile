FROM python:3.12-slim

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    IN_DOCKER=1 \
    POETRY_VIRTUALENVS_CREATE=false

WORKDIR /app

# Install Poetry for dependency management
RUN pip install --no-cache-dir poetry

# Copy dependency manifests first for efficient Docker layer caching
COPY pyproject.toml poetry.lock* ./

# Install both runtime and dev dependencies into the image environment
# Dev deps include pytest to allow `docker run <image> pytest -q`
RUN poetry install --no-interaction --no-ansi --with dev --no-root

# Copy the rest of the project files
COPY . .

CMD ["python", "main.py"]
