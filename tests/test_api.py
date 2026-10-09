"""
Unit tests untuk API Apotek Demand Forecast.
Jalankan: pytest tests/test_api.py -v
"""
import pytest
from fastapi.testclient import TestClient
import sys
import os

# Tambahkan root project ke sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from api.main import app
from api import model_loader

# Load model dulu sebelum test
model_loader.load_all_models()

# TestClient untuk simulasi request HTTP
client = TestClient(app)


# ============================================================
# TEST 1: ROOT ENDPOINT
# ============================================================
def test_root():
    """Test endpoint / (root)"""
    response = client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert "message" in data
    assert "Apotek" in data["message"]


# ============================================================
# TEST 2: HEALTH CHECK
# ============================================================
def test_health():
    """Test endpoint /health — pastikan 12 model ke-load"""
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "ok"
    assert data["models_loaded"] == 12
    assert len(data["categories"]) == 12


# ============================================================
# TEST 3: LIST CATEGORIES
# ============================================================
def test_categories():
    """Test endpoint /categories — pastikan ada 12 kategori"""
    response = client.get("/categories")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) == 12
    assert "Alergi" in data


# ============================================================
# TEST 4: CATEGORY DETAIL
# ============================================================
def test_category_detail():
    """Test endpoint /categories/{kategori}"""
    response = client.get("/categories/Alergi")
    assert response.status_code == 200
    data = response.json()
    assert data["kategori"] == "Alergi"
    assert "avg_weekly" in data
    assert "last_date" in data


def test_category_detail_invalid():
    """Test /categories/{kategori} dengan kategori tidak ada → 404"""
    response = client.get("/categories/KategoriTidakAda")
    assert response.status_code == 404


# ============================================================
# TEST 5: PREDICT — VALID
# ============================================================
def test_predict_valid():
    """Test endpoint /predict dengan kategori valid"""
    response = client.post(
        "/predict",
        json={"kategori": "Alergi", "buffer_pct": 20},
    )
    assert response.status_code == 200
    data = response.json()
    assert data["kategori"] == "Alergi"
    assert "predicted_qty" in data
    assert "recommendation_restock" in data
    assert data["predicted_qty"] > 0
    assert data["recommendation_restock"] > data["predicted_qty"]  # buffer 20%


# ============================================================
# TEST 6: PREDICT — BUFFER BERBEDA
# ============================================================
def test_predict_buffer_zero():
    """Buffer 0% → rekomendasi = prediksi"""
    response = client.post(
        "/predict",
        json={"kategori": "Alergi", "buffer_pct": 0},
    )
    assert response.status_code == 200
    data = response.json()
    # Prediksi & rekomendasi harus sama (selisih < 1 karena rounding)
    assert abs(data["predicted_qty"] - data["recommendation_restock"]) < 1


def test_predict_buffer_50():
    """Buffer 50% → rekomendasi = prediksi × 1.5"""
    response = client.post(
        "/predict",
        json={"kategori": "Alergi", "buffer_pct": 50},
    )
    assert response.status_code == 200
    data = response.json()
    expected = data["predicted_qty"] * 1.5
    assert abs(data["recommendation_restock"] - expected) < 1


# ============================================================
# TEST 7: PREDICT — INVALID
# ============================================================
def test_predict_invalid_kategori():
    """Kategori tidak ada → 404"""
    response = client.post(
        "/predict",
        json={"kategori": "KategoriPalsu", "buffer_pct": 20},
    )
    assert response.status_code == 404


def test_predict_invalid_buffer():
    """Buffer di luar range (0-100) → 422 validation error"""
    response = client.post(
        "/predict",
        json={"kategori": "Alergi", "buffer_pct": 150},
    )
    assert response.status_code == 422


# ============================================================
# TEST 8: HISTORY
# ============================================================
def test_history():
    """Test endpoint /history"""
    response = client.get("/history?limit=5")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)


# ============================================================
# TEST 9: SEMUA KATEGORI BISA DIPREDIKSI
# ============================================================
def test_predict_all_categories():
    """Pastikan SEMUA 12 kategori bisa diprediksi tanpa error"""
    categories_response = client.get("/categories")
    categories = categories_response.json()

    for cat in categories:
        response = client.post(
            "/predict",
            json={"kategori": cat, "buffer_pct": 20},
        )
        assert response.status_code == 200, f"Gagal prediksi kategori: {cat}"
        data = response.json()
        assert data["predicted_qty"] > 0, f"Prediksi 0 untuk: {cat}"