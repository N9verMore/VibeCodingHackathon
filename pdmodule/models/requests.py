# ============================================
# FILE: pdmodule/models/requests.py
# ============================================
from pydantic import BaseModel
from typing import Optional


class ProcessReviewsRequest(BaseModel):
    """Request body для обробки відгуків"""
    brand: str
    
    class Config:
        json_schema_extra = {
            "example": {
                "brand": "TestBrand"
            }
        }
