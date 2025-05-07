FROM python:3.11-slim

WORKDIR /app

# Install dependencies and required system packages
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    gcc \
    python3-dev && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

# Copy requirements and install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Set cache directories to avoid /.cache
ENV TRANSFORMERS_CACHE=/tmp/hf_cache
ENV HF_HOME=/tmp/hf_home

# Download the model as root
RUN python3 -c "from sentence_transformers import SentenceTransformer; SentenceTransformer('all-MiniLM-L6-v2')"

COPY app.py .

# Create non-root user and fix permissions
RUN useradd -m appuser && \
    chown -R appuser /tmp/hf_cache /tmp/hf_home /app

USER appuser

ENV HOST=0.0.0.0
ENV PORT=8000
ENV MODEL_NAME=all-MiniLM-L6-v2

EXPOSE 8000

CMD ["gunicorn", "app:app", "--workers", "2", "--worker-class", "uvicorn.workers.UvicornWorker", "--bind", "0.0.0.0:8000"]
