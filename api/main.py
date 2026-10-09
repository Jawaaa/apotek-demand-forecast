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
from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from typing import List

from . import model_loader, schemas
from .database import get_db, PredictionLog

# ===== Inisialisasi FastAPI =====
app = FastAPI(
    title="Apotek Demand Forecast API",
    description="API untuk memprediksi demand obat mingguan per kategori menggunakan LSTM",
    version="1.0.0",
)

# ===== CORS =====
# Biar Streamlit (atau aplikasi lain) bisa akses API dari domain berbeda
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Ganti dengan domain spesifik nanti di production
    allow_methods=["*"],
    allow_headers=["*"],
)


# ===== Startup Event =====
@app.on_event("startup")
def startup_event():
    """Load semua model saat API pertama kali jalan."""
    print("Loading models...")
    model_loader.load_all_models()
    print("API siap!")


# ===== Endpoints =====

@app.get("/")
def root():
    """Endpoint root — untuk cek API hidup."""
    return {
        "message": "Apotek Demand Forecast API",
        "docs": "/docs",
        "version": "1.0.0"
    }


@app.get("/health", response_model=schemas.HealthResponse)
def health_check():
    """Cek status API & berapa model yang ke-load."""
    return {
        "status": "ok",
        "models_loaded": len(model_loader.get_categories()),
        "categories": model_loader.get_categories(),
    }


@app.get("/categories", response_model=List[str])
def list_categories():
    """Daftar semua kategori yang tersedia."""
    return model_loader.get_categories()


@app.get("/categories/{kategori}", response_model=schemas.CategoryInfo)
def category_detail(kategori: str):
    """Info detail untuk 1 kategori."""
    try:
        return model_loader.get_category_info(kategori)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


@app.post("/predict", response_model=schemas.PredictionResponse)
def predict(request: schemas.PredictionRequest, db: Session = Depends(get_db)):
    """
    Prediksi demand minggu depan + rekomendasi restock.
    Hasil otomatis disimpan ke database.
    """
    try:
        result = model_loader.predict_next_week(
            kategori=request.kategori,
            buffer_pct=request.buffer_pct,
        )
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))

    # Simpan ke database
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
    """Ambil riwayat prediksi terakhir."""
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