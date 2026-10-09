"""
Database setup menggunakan SQLAlchemy + SQLite.
SQLite dipilih karena ringan, tidak perlu server, dan 1 file saja.
"""
from sqlalchemy import create_engine, Column, Integer, String, Float, DateTime
from sqlalchemy.orm import declarative_base, sessionmaker
from datetime import datetime

# SQLite database file
DATABASE_URL = "sqlite:///./predictions.db"

# Engine: koneksi ke database
engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False}  # khusus SQLite + FastAPI
)

# Session: untuk transaksi (insert, query)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base: parent class untuk tabel
Base = declarative_base()


class PredictionLog(Base):
    """
    Tabel untuk menyimpan setiap prediksi yang dilakukan.
    Ini untuk audit trail & analisis ke depan.
    """
    __tablename__ = "prediction_logs"

    id = Column(Integer, primary_key=True, index=True)
    kategori = Column(String, index=True)
    predicted_qty = Column(Float)
    recommendation_restock = Column(Float)
    buffer_pct = Column(Float, default=20.0)
    created_at = Column(DateTime, default=datetime.utcnow)


# Buat tabel kalau belum ada
Base.metadata.create_all(bind=engine)


def get_db():
    """
    Dependency untuk FastAPI.
    Setiap request dapat session baru, lalu ditutup otomatis.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()