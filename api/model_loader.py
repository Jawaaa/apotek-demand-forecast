"""
Load semua model LSTM & scaler saat API startup.
Model di-load sekali saja (bukan setiap request) supaya cepat.
"""
import os
import joblib
import numpy as np
from tensorflow.keras.models import load_model

# Path ke folder models
MODELS_DIR = os.path.join(os.path.dirname(__file__), "..", "models")

# Cache global
_models = {}
_scalers = {}
_metadata = None
_categories = []


def load_all_models():
    """
    Load semua model .h5 + scaler .pkl + metadata.pkl.
    Dipanggil SEKALI saat API startup.
    """
    global _metadata, _categories

    metadata_path = os.path.join(MODELS_DIR, "metadata.pkl")
    if not os.path.exists(metadata_path):
        raise FileNotFoundError(f"metadata.pkl tidak ditemukan di {MODELS_DIR}")

    _metadata = joblib.load(metadata_path)
    _categories = list(_metadata.keys())

    for cat, info in _metadata.items():
        safe_name = info["safe_name"]

        # Load model
        model_path = os.path.join(MODELS_DIR, f"model_{safe_name}.keras")
        _models[cat] = load_model(model_path, compile=False)

        # Load scaler
        scaler_path = os.path.join(MODELS_DIR, f"scaler_{safe_name}.pkl")
        _scalers[cat] = joblib.load(scaler_path)

    print(f"[OK] Loaded {len(_models)} models untuk kategori: {_categories}")


def predict_next_week(kategori: str, buffer_pct: float = 20.0):
    """
    Prediksi demand minggu depan untuk 1 kategori.
    Return: dict berisi prediksi & rekomendasi restock.
    """
    if kategori not in _models:
        raise ValueError(f"Kategori '{kategori}' tidak ditemukan. Pilihan: {_categories}")

    info = _metadata[kategori]
    model = _models[kategori]
    scaler = _scalers[kategori]

    # Ambil LOOKBACK minggu terakhir
    last_values = np.array(info["last_values"]).reshape(-1, 1)

    # Scale
    scaled = scaler.transform(last_values).flatten()

    # Reshape jadi (1, LOOKBACK, 1) untuk LSTM
    seq = scaled.reshape(1, -1, 1)

    # Prediksi
    pred_scaled = model.predict(seq, verbose=0).flatten()[0]

    # Inverse transform
    pred_inv = scaler.inverse_transform([[pred_scaled]])[0, 0]
    pred_inv = max(pred_inv, 0)

    # Rekomendasi restock dengan buffer
    rekomendasi = pred_inv * (1 + buffer_pct / 100)

    return {
        "kategori": kategori,
        "predicted_qty": round(float(pred_inv), 1),
        "recommendation_restock": round(float(rekomendasi), 1),
        "buffer_pct": buffer_pct,
        "last_date": info["last_date"],
    }


def get_categories():
    """Return daftar kategori yang tersedia."""
    return _categories


def get_category_info(kategori: str):
    """Return info detail 1 kategori."""
    if kategori not in _metadata:
        raise ValueError(f"Kategori '{kategori}' tidak ditemukan")

    info = _metadata[kategori]
    return {
        "kategori": kategori,
        "total_weeks": len(info["last_values"]) + 7,  # estimasi
        "avg_weekly": round(info["mean"], 1),
        "min_qty": round(info["min"], 1),
        "max_qty": round(info["max"], 1),
        "last_date": info["last_date"],
    }


def get_metadata():
    """Return seluruh metadata."""
    return _metadata