FROM python:3.9-slim

ENV QUART_ENV=production

COPY requirements.txt /app/requirements.txt
COPY .env /app/.env

WORKDIR /app

RUN pip install -r requirements.txt

COPY src/ /app

CMD ["hypercorn", "--bind=0.0.0.0:5000", "app:app"]
