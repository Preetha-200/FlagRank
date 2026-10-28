FROM python:3.12-slim

WORKDIR /app

# Install system dependencies if needed
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application and research framework
COPY api/ ./api/
COPY research_framework/ ./research_framework/

ENV PYTHONUNBUFFERED=1
ENV HOST=0.0.0.0
ENV PORT=8000
ENV MAX_UPLOAD_SIZE_MB=50
ENV CORS_ORIGINS=*

EXPOSE 8000

CMD ["sh", "-c", "python -m uvicorn api.server:app --host ${HOST:-0.0.0.0} --port ${PORT:-8000}"]
