"""
Unit tests untuk API Apotek Demand Forecast.
Jalankan: pytest tests/test_api.py -v
"""
import os
import sys
import pytest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

MODELS_DIR = os.path.join(os.path.dirname(__file__), "..", "models")
MODEL_EXISTS = os.path.exists(os.path.join(MODELS_DIR, "metadata.pkl"))

pytestmark = pytest.mark.skipif(
    not MODEL_EXISTS,
    reason="Model files tidak tersedia (di-ignore di Git). Test di-skip di CI/CD."
)

if MODEL_EXISTS:
    from fastapi.testclient import TestClient
    from api.main import app
    from api import model_loader

    model_loader.load_all_models()
    client = TestClient(app)


def test_root():
    response = client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert "message" in data
    assert "Apotek" in data["message"]


def test_health():
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "ok"
    assert data["models_loaded"] == 12
    assert len(data["categories"]) == 12


def test_categories():
    response = client.get("/categories")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) == 12
    assert "Alergi" in data


def test_category_detail():
    response = client.get("/categories/Alergi")
    assert response.status_code == 200
    data = response.json()
    assert data["kategori"] == "Alergi"
    assert "avg_weekly" in data
    assert "last_date" in data
    assert "total_weeks" in data


def test_category_detail_invalid():
    response = client.get("/categories/KategoriTidakAda")
    assert response.status_code == 404


def test_predict_valid():
    response = client.post("/predict", json={"kategori": "Alergi", "buffer_pct": 20})
    assert response.status_code == 200
    data = response.json()
    assert data["kategori"] == "Alergi"
    assert data["predicted_qty"] > 0
    assert data["recommendation_restock"] > data["predicted_qty"]


def test_predict_buffer_zero():
    response = client.post("/predict", json={"kategori": "Alergi", "buffer_pct": 0})
    assert response.status_code == 200
    data = response.json()
    assert abs(data["predicted_qty"] - data["recommendation_restock"]) < 1


def test_predict_buffer_50():
    response = client.post("/predict", json={"kategori": "Alergi", "buffer_pct": 50})
    assert response.status_code == 200
    data = response.json()
    expected = data["predicted_qty"] * 1.5
    assert abs(data["recommendation_restock"] - expected) < 1


def test_predict_invalid_kategori():
    response = client.post("/predict", json={"kategori": "KategoriPalsu", "buffer_pct": 20})
    assert response.status_code == 404


def test_predict_invalid_buffer():
    response = client.post("/predict", json={"kategori": "Alergi", "buffer_pct": 150})
    assert response.status_code == 422


def test_history():
    response = client.get("/history?limit=5")
    assert response.status_code == 200
    assert isinstance(response.json(), list)


def test_predict_all_categories():
    categories = client.get("/categories").json()
    for cat in categories:
        response = client.post("/predict", json={"kategori": cat, "buffer_pct": 20})
        assert response.status_code == 200, f"Gagal prediksi kategori: {cat}"
        assert response.json()["predicted_qty"] > 0, f"Prediksi 0 untuk: {cat}"


# TEST BARU: pastikan reshape model memakai lookback dari metadata
def test_predict_uses_metadata_lookback():
    """Kalau model_loader salah reshape (hardcode lookback=2), test ini akan gagal
    saat lookback hasil tuning ternyata bukan 2."""
    for cat in client.get("/categories").json():
        r = client.post("/predict", json={"kategori": cat, "buffer_pct": 20})
        assert r.status_code == 200, f"lookback mismatch di kategori {cat}"