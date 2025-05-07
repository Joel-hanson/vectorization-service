# Vectorization Service

A production-ready REST API service for converting text to vector embeddings, built for Kubernetes deployment.

## Overview

This service provides a simple REST API endpoint to convert input text into vector embeddings using the SentenceTransformer library. It's designed for production use with:

- FastAPI for efficient API handling
- Gunicorn for production WSGI serving
- Kubernetes deployment configuration
- Containerized with Docker
- Health checks and readiness probes
- Horizontal pod autoscaling

## API Endpoints

### POST /vectorize

Convert text to vector embeddings.

**Request:**

```json
{
  "text": "This is an example text to vectorize"
}
```

or for batch processing:

```json
{
  "text": ["This is the first text", "This is the second text"]
}
```

**Response:**

```json
{
  "vector": [[0.1, 0.2, ..., 0.3], ...],
  "dimensions": 384,
  "model": "all-MiniLM-L6-v2"
}
```

### GET /health

Check service health status.

**Response:**

```json
{
  "status": "ok",
  "model": "all-MiniLM-L6-v2"
}
```

## Getting Started

### Local Development

1. Install dependencies:

   ```bash
   pip install -r requirements.txt
   ```

2. Run the service:

   ```bash
   python app.py
   ```

3. Access the API documentation at <http://localhost:8000/docs>

### Docker

1. Build the Docker image:

   ```bash
   docker build -t vectorization-service:latest .
   ```

2. Run the container:

   ```bash
   docker run -p 8000:8000 vectorization-service:latest
   ```

### Kubernetes Deployment

1. Update the image path in `deployment/k8s/deployment.yml` or for openshift `deployment/openshift/deployment.yml`

2. Apply the Kubernetes configurations:

   ```bash
   kubectl apply -f deployment/k8s/deployment.yml
   kubectl apply -f deployment/k8s/hpa.yml
   ```

for openshift:

   ```bash
   oc apply -f deployment/openshift/deployment.yml
   oc apply -f deployment/openshift/hpa.yml
   ```

## Configuration

The service can be configured using environment variables:

- `MODEL_NAME`: The SentenceTransformer model to use (default: "all-MiniLM-L6-v2")
- `HOST`: Host to bind the service to (default: "0.0.0.0")
- `PORT`: Port to run the service on (default: 8000)

## Performance Considerations

- The service uses Gunicorn with multiple workers for better concurrency
- Model is downloaded during Docker build for faster startup
- Memory and CPU limits are set in Kubernetes config
- Horizontal pod autoscaling is configured for handling varying loads

## Security Notes

- The Docker container runs as a non-root user
- CORS is enabled but should be configured for production
- Input validation is performed using Pydantic models

## Load Testing

Before production deployment, it's recommended to load test the service with tools like:

- Apache JMeter
- Locust
- k6

## License

Licensed under the Apache License, Version 2.0 (the "License"); you may not use this file except in compliance with the License. You may obtain a copy of the License at

<http://www.apache.org/licenses/LICENSE-2.0>
