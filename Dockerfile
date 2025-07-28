
FROM python:3.9-alpine

WORKDIR /app

COPY requirements.txt .

RUN apk add --no-cache gcc musl-dev libstdc++ g++ && \
    pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt && \
    apk del gcc musl-dev g++

COPY extract_outline.py .

ENTRYPOINT ["python", "extract_outline.py"]

CMD ["--input-dir", "/app/input", "--output-dir", "/app/output"]
