FROM python:3.12-slim

ENV POETRY_VERSION=2.2.1 \
    PYTHONUNBUFFERED=1

RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    gcc \
    libpq-dev \
    curl \
    && rm -rf /var/lib/apt/lists/*

RUN pip install "poetry==$POETRY_VERSION"
RUN poetry config virtualenvs.create false

WORKDIR /app

COPY pyproject.toml poetry.lock ./

RUN poetry install --only main --no-root

COPY src/ src/
COPY input/ input/

# Add a user that is not root
RUN adduser --system --no-create-home nonroot
USER nonroot

EXPOSE 8000

ENV PYTHONPATH=/app/src
ENV FILE_PATH_ENERGY_PRICES='/app/input/energy_prices/energy_prices_2024.csv'
ENV FILE_PATH_BASELOADS='/app/input/ko_profiles/'

CMD ["uvicorn", "src.app:app", "--host", "0.0.0.0", "--port", "8000"]
