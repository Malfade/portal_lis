FROM python:3.12-slim-bookworm

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY licensing ./licensing
COPY templates ./templates

RUN mkdir -p /data

ENV LICENSING_DATABASE_URL=sqlite:////data/licensing.db
ENV PYTHONUNBUFFERED=1

EXPOSE 8080

CMD ["uvicorn", "licensing.main:app", "--host", "0.0.0.0", "--port", "8080"]
