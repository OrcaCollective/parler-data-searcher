FROM python:3.9-slim

ENV QUART_ENV=production
ENV PYTHONUNBUFFERED=1
ENV PIP_NO_CACHE_DIR=1

WORKDIR /app

RUN mkdir app

COPY pyproject.toml /app
COPY poetry.lock /app

RUN pip3 install poetry
RUN poetry config virtualenvs.create false
RUN poetry install --no-dev

COPY src/ /app

CMD ["hypercorn", "--bind=0.0.0.0:5000", "--workers=4", "app:app"]
