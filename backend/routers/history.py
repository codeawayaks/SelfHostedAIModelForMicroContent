"""
API router for generation history endpoints
"""
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import desc
from typing import Optional
from backend.models import schemas
from backend.models.database import get_db, Generation

router = APIRouter(prefix="/api/history", tags=["history"])


@router.get("", response_model=schemas.HistoryResponse)
def get_history(
    page: int = Query(1, ge=1),
    page_size: int = Query(10, ge=1, le=100),
    db: Session = Depends(get_db)
):
    """
    Get paginated list of generation history
    """
    try:
        # Calculate offset
        offset = (page - 1) * page_size
        
        # Get total count
        total = db.query(Generation).count()
        
        # Get paginated results
        generations = db.query(Generation)\
            .order_by(desc(Generation.timestamp))\
            .offset(offset)\
            .limit(page_size)\
            .all()
        
        items = [schemas.GenerationListItem(
            id=gen.id,
            input_type=gen.input_type,
            input_content=gen.input_content,
            final_output=gen.final_output,
            cost=gen.cost,
            timestamp=gen.timestamp
        ) for gen in generations]
        
        return schemas.HistoryResponse(
            items=items,
            total=total,
            page=page,
            page_size=page_size
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to retrieve history: {str(e)}")


@router.get("/{generation_id}", response_model=schemas.GenerationResponse)
def get_generation(
    generation_id: int,
    db: Session = Depends(get_db)
):
    """
    Get specific generation by ID
    """
    generation = db.query(Generation).filter(Generation.id == generation_id).first()
    
    if not generation:
        raise HTTPException(status_code=404, detail="Generation not found")
    
    return generation


@router.delete("/{generation_id}")
def delete_generation(
    generation_id: int,
    db: Session = Depends(get_db)
):
    """
    Delete a generation record
    """
    generation = db.query(Generation).filter(Generation.id == generation_id).first()
    
    if not generation:
        raise HTTPException(status_code=404, detail="Generation not found")
    
    try:
        db.delete(generation)
        db.commit()
        return {"message": "Generation deleted successfully"}
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Failed to delete generation: {str(e)}")

