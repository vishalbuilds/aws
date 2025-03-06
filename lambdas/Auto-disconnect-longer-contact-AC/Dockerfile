
FROM python:3.9-slim

WORKDIR /app

LABEL application="sample"

COPY src/requirements.txt .

RUN pip install --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt


COPY . .
COPY test.sh .

ENV PYTHONPATH=/app

RUN chmod +x test.sh

RUN ["./test.sh"]

