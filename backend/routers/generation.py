"""
API router for post generation endpoints
"""
import logging
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from backend.models import schemas
from backend.models.database import get_db, Generation
from backend.services.orchestration import OrchestrationService
from datetime import datetime

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/generate", tags=["generation"])


@router.post("", response_model=schemas.GenerationResponse)
async def generate_post(
    request: schemas.GenerationRequest,
    db: Session = Depends(get_db)
):
    """
    Generate a complete social media post
    
    Steps:
    1. Hook Generation (Phi-2)
    2. Caption Generation (Mistral 7B)
    3. CTA Generation (Phi-2)
    4. Merge & Output
    """
    try:
        # Initialize orchestration service
        orchestration = OrchestrationService()
        
        # Generate post
        result = await orchestration.generate_post(
            input_type=request.input_type,
            input_content=request.input_content
        )
        
        # Save to database
        generation = Generation(
            input_type=request.input_type,
            input_content=request.input_content,
            hook=result["hook"],
            caption=result["caption"],
            cta=result["cta"],
            final_output=result["final_output"],
            cost=result["cost"],
            hook_cost=result["hook_cost"],
            caption_cost=result["caption_cost"],
            cta_cost=result["cta_cost"],
            merge_cost=result["merge_cost"],
            timestamp=datetime.utcnow()
        )
        
        db.add(generation)
        db.commit()
        db.refresh(generation)
        
        return generation
        
    except ValueError as e:
        # Configuration validation errors
        db.rollback()
        logger.error(f"Configuration error: {str(e)}")
        raise HTTPException(status_code=400, detail=f"Configuration error: {str(e)}")
    except Exception as e:
        # Log full error for debugging
        db.rollback()
        logger.exception(f"Generation failed: {str(e)}")
        error_message = str(e)
        # Provide more helpful error messages
        if "RUNPOD" in error_message.upper() or "API_KEY" in error_message.upper():
            error_message = f"Runpod configuration error: {error_message}. Please check your .env file."
        elif "endpoint" in error_message.lower():
            error_message = f"Runpod endpoint error: {error_message}. Please verify your endpoint IDs are correct."
        raise HTTPException(status_code=500, detail=f"Generation failed: {error_message}")

