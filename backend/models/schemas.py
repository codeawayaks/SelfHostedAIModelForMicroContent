from pydantic import BaseModel
from typing import Optional, Literal
from datetime import datetime


class GenerationRequest(BaseModel):
    input_type: Literal["topic", "prompt"]
    input_content: str


class GenerationResponse(BaseModel):
    id: int
    input_type: str
    input_content: str
    hook: Optional[str]
    caption: Optional[str]
    cta: Optional[str]
    final_output: str
    cost: float
    hook_cost: float
    caption_cost: float
    cta_cost: float
    merge_cost: float
    timestamp: datetime
    
    class Config:
        from_attributes = True


class GenerationListItem(BaseModel):
    id: int
    input_type: str
    input_content: str
    final_output: str
    cost: float
    timestamp: datetime
    
    class Config:
        from_attributes = True


class HistoryResponse(BaseModel):
    items: list[GenerationListItem]
    total: int
    page: int
    page_size: int

