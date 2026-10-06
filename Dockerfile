FROM python:3.12-slim AS runtime

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1

WORKDIR /app

COPY pyproject.toml README.md LICENSE ./
COPY src ./src
RUN pip install --upgrade pip && pip install .

RUN useradd --create-home --uid 10001 veritrag && chown -R veritrag:veritrag /app
USER veritrag

EXPOSE 8000
CMD ["uvicorn", "veritrag.api.app:app", "--host", "0.0.0.0", "--port", "8000"]
