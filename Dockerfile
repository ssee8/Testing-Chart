FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app

COPY server.py ./server.py
COPY public/ ./public/

RUN useradd --system --uid 10001 --create-home app \
    && mkdir -p /app/public/videos /app/submissions \
    && chown -R app:app /app

USER app

EXPOSE 8080

CMD ["python", "server.py"]
