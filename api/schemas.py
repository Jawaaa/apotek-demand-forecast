"""
Pydantic schemas — mendefinisikan struktur request & response API.
FastAPI pakai ini untuk VALIDASI OTOMATIS.
"""
from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime


class PredictionRequest(BaseModel):
    """Request body untuk endpoint /predict"""
    kategori: str = Field(..., description="Nama kategori obat", example="Alergi")
    buffer_pct: float = Field(20.0, ge=0, le=100, description="Buffer safety stock dalam %")

    class Config:
        json_schema_extra = {
            "example": {
                "kategori": "Alergi",
                "buffer_pct": 20.0
            }
        }


class PredictionResponse(BaseModel):
    """Response untuk endpoint /predict"""
    kategori: str
    predicted_qty: float
    recommendation_restock: float
    buffer_pct: float
    last_date: str
    message: str


class CategoryInfo(BaseModel):
    """Info satu kategori"""
    kategori: str
    total_weeks: int
    avg_weekly: float
    min_qty: float
    max_qty: float
    last_date: str


class HealthResponse(BaseModel):
    """Response untuk /health"""
    status: str
    models_loaded: int
    categories: List[str]