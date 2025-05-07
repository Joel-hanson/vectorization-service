"""
Vectorization Service API
-------------------------
A REST API that converts text to vector embeddings.
"""
import logging
import os
from typing import Dict, List, Optional, Union

import numpy as np
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from sentence_transformers import SentenceTransformer

# Configure logging
logging.basicConfig(
    format="%(asctime)s %(levelname)s: %(message)s",
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Create FastAPI app
app = FastAPI(
    title="Vectorization Service",
    description="API for converting text to vector embeddings",
    version="1.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Modify in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Load environment variables
MODEL_NAME = os.getenv("MODEL_NAME", "all-MiniLM-L6-v2")


class TextInput(BaseModel):
    """Input model for text to be vectorized."""
    text: Union[str, List[str]]


class VectorOutput(BaseModel):
    """Output model for vectorization results."""
    vector: List[List[float]]
    dimensions: int
    model: str


class HealthResponse(BaseModel):
    """Health check response."""
    status: str
    model: str


class VectorizationService:
    """Service for text vectorization."""

    def __init__(self, model_name: str):
        """Initialize the vectorization service with a model."""
        logger.info(f"Loading model: {model_name}")
        self.model_name = model_name
        self.model = SentenceTransformer(model_name)
        logger.info(f"Model loaded successfully. Vector size: {self.model.get_sentence_embedding_dimension()}")

    def vectorize(self, text: Union[str, List[str]]) -> np.ndarray:
        """Convert text to vector embeddings."""
        try:
            # Handle both single text and list of texts
            if isinstance(text, str):
                text = [text]

            # Generate embeddings and convert to Python list for JSON serialization
            embeddings = self.model.encode(text)
            return embeddings
        except Exception as e:
            logger.error(f"Vectorization error: {str(e)}")
            raise HTTPException(status_code=500, detail=f"Vectorization failed: {str(e)}")


# Initialize service
service = VectorizationService(MODEL_NAME)


@app.post("/vectorize", response_model=VectorOutput)
async def vectorize_endpoint(input_data: TextInput) -> Dict:
    """
    Convert text to vector embeddings.

    - Accepts a single text string or list of strings
    - Returns vector embeddings for each text
    """
    embeddings = service.vectorize(input_data.text)

    # Convert numpy arrays to lists for JSON serialization
    embeddings_list = embeddings.tolist()

    return {
        "vector": embeddings_list,
        "dimensions": len(embeddings_list[0]) if embeddings_list else 0,
        "model": service.model_name
    }


@app.get("/health", response_model=HealthResponse)
async def health_check() -> Dict:
    """Check if the service is healthy."""
    return {
        "status": "ok",
        "model": service.model_name
    }


if __name__ == "__main__":
    import uvicorn
    # Use environment variables or defaults
    host = os.getenv("HOST", "0.0.0.0")
    port = int(os.getenv("PORT", "8000"))

    logger.info(f"Starting vectorization service on {host}:{port}")
    uvicorn.run("app:app", host=host, port=port, reload=False)