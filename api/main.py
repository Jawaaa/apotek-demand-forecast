"""
FastAPI main app.
Endpoint:
  GET  /              -> welcome
  GET  /health        -> cek status API
  GET  /categories    -> daftar kategori
  GET  /categories/{kategori}  -> info 1 kategori
  POST /predict       -> prediksi demand + rekomendasi restock
  GET  /history       -> riwayat prediksi (dari database)
"""
from contextlib import asynccontextmanager
from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from typing import List

from . import model_loader, schemas
from .database import get_db, PredictionLog


@asynccontextmanager
async def lifespan(app: FastAPI):
    print("Loading models...")
    model_loader.load_all_models()
    print("API siap!")
    yield


app = FastAPI(
    title="Apotek Demand Forecast API",
    description="API untuk memprediksi demand obat mingguan per kategori menggunakan LSTM",
    version="1.0.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
def root():
    return {
        "message": "Apotek Demand Forecast API",
        "docs": "/docs",
        "version": "1.0.0",
    }


@app.get("/health", response_model=schemas.HealthResponse)
def health_check():
    return {
        "status": "ok",
        "models_loaded": len(model_loader.get_categories()),
        "categories": model_loader.get_categories(),
    }


@app.get("/categories", response_model=List[str])
def list_categories():
    return model_loader.get_categories()


@app.get("/categories/{kategori}", response_model=schemas.CategoryInfo)
def category_detail(kategori: str):
    try:
        return model_loader.get_category_info(kategori)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


@app.post("/predict", response_model=schemas.PredictionResponse)
def predict(request: schemas.PredictionRequest, db: Session = Depends(get_db)):
    try:
        result = model_loader.predict_next_week(
            kategori=request.kategori,
            buffer_pct=request.buffer_pct,
        )
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))

    log = PredictionLog(
        kategori=result["kategori"],
        predicted_qty=result["predicted_qty"],
        recommendation_restock=result["recommendation_restock"],
        buffer_pct=result["buffer_pct"],
    )
    db.add(log)
    db.commit()
    db.refresh(log)

    return {
        **result,
        "message": f"Prediksi untuk {result['kategori']} berhasil disimpan (log id: {log.id})",
    }


@app.get("/history")
def get_history(limit: int = 20, db: Session = Depends(get_db)):
    logs = (
        db.query(PredictionLog)
        .order_by(PredictionLog.created_at.desc())
        .limit(limit)
        .all()
    )
    return [
        {
            "id": log.id,
            "kategori": log.kategori,
            "predicted_qty": log.predicted_qty,
            "recommendation_restock": log.recommendation_restock,
            "buffer_pct": log.buffer_pct,
            "created_at": log.created_at.isoformat(),
        }
        for log in logs
    ]