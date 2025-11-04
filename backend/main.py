"""
FastAPI application entry point
"""
import logging
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from backend.routers import generation, history
from backend.models.database import init_db

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
# Enable debug logging for runpod client to see detailed request/response info
logging.getLogger("backend.services.runpod_client").setLevel(logging.DEBUG)

# Initialize database
init_db()

# Create FastAPI app
app = FastAPI(
    title="Runpod Text Models Integration",
    description="API for generating social media posts using Runpod.io models",
    version="1.0.0"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify actual frontend URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(generation.router)
app.include_router(history.router)


@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "Runpod Text Models Integration API",
        "version": "1.0.0",
        "endpoints": {
            "generate": "/api/generate",
            "history": "/api/history"
        }
    }


@app.get("/health")
async def health():
    """Health check endpoint"""
    return {"status": "healthy"}


@app.get("/api/test-runpod")
async def test_runpod():
    """Test Runpod endpoint connectivity"""
    try:
        from backend.services.runpod_client import RunpodClient
        client = RunpodClient()
        
        # Test with a simple prompt
        test_result = await client.generate_text(
            "Say hello in one word",
            model_type="phi2",
            max_tokens=10
        )
        
        return {
            "status": "success",
            "message": "Runpod endpoint is working",
            "test_response": test_result
        }
    except Exception as e:
        return {
            "status": "error",
            "message": str(e)
        }


@app.get("/api/check-job/{endpoint_id}/{job_id}")
async def check_job_status(endpoint_id: str, job_id: str):
    """Check the status of a Runpod job"""
    try:
        import httpx
        from backend.config import get_settings
        
        settings = get_settings()
        status_url = f"https://api.runpod.ai/v2/{endpoint_id}/status/{job_id}"
        
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {settings.runpod_api_key}"
        }
        
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.get(status_url, headers=headers)
            response.raise_for_status()
            result = response.json()
            
            return {
                "status": "success",
                "job_id": job_id,
                "job_status": result
            }
    except Exception as e:
        return {
            "status": "error",
            "message": str(e)
        }

