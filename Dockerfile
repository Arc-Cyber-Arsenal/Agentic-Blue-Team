FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_INDEX_URL=https://pypi.org/simple

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends curl \
    && rm -rf /var/lib/apt/lists/*

COPY pyproject.toml README.md ./
COPY ABT ./ABT
COPY Core ./Core
COPY Lib ./Lib
COPY MODULES ./MODULES
COPY PLAYBOOKS ./PLAYBOOKS
COPY PLUGINS ./PLUGINS
COPY DATA ./DATA
COPY AGENTS ./AGENTS
COPY bootstrap.py ./

RUN pip install torch --index-url https://download.pytorch.org/whl/cpu \
    && pip install -e .

RUN python bootstrap.py

EXPOSE 8000

CMD ["sh", "-c", "python manage.py migrate --noinput && python -m uvicorn ABT.asgi:application --host 0.0.0.0 --port 8000"]
