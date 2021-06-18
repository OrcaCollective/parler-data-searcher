FROM python:3.9-slim

ENV PYTHONUNBUFFERED=true \
    QUART_DEBUG=1

COPY requirements.txt /app/requirements.txt

WORKDIR /app

RUN pip install -r requirements.txt

COPY src/ /app

CMD ["python", "app.py"]
