FROM python:3.12-bookworm AS builder

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1
WORKDIR /app

RUN pip install poetry
RUN poetry config virtualenvs.in-project true
COPY pyproject.toml poetry.lock ./
RUN poetry install
FROM python:3.12-slim-bookworm
WORKDIR /app
COPY --from=builder /app/.venv .venv/
COPY . .

RUN ls -R /app

ENV VIRTUAL_ENV /app/.venv
ENV PATH /app/.venv/bin:$PATH
RUN which python
# CMD ["ls", "-R", "/app"]
CMD ["python", "lichess-bot.py", "-v"]