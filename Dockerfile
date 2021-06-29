FROM python:3.9-slim

ENV QUART_ENV=production
ENV PYTHONUNBUFFERED=1
ENV PIP_NO_CACHE_DIR=1

COPY requirements.txt /app/requirements.txt

WORKDIR /app

RUN pip install -r requirements.txt

COPY src/ /app
COPY bin/ /app/bin

CMD ["./bin/run.sh"]
