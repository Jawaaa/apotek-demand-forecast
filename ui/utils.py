"""
Helper functions untuk Streamlit UI.
"""
import requests
import pandas as pd
import os

API_BASE_URL = "http://127.0.0.1:8000"


def get_categories():
    try:
        r = requests.get(f"{API_BASE_URL}/categories", timeout=10)
        r.raise_for_status()
        return r.json()
    except Exception as e:
        return {"error": str(e)}


def predict(kategori: str, buffer_pct: float = 20.0):
    try:
        r = requests.post(
            f"{API_BASE_URL}/predict",
            json={"kategori": kategori, "buffer_pct": buffer_pct},
            timeout=30,
        )
        r.raise_for_status()
        return r.json()
    except Exception as e:
        return {"error": str(e)}


def get_history(limit: int = 20):
    try:
        r = requests.get(f"{API_BASE_URL}/history?limit={limit}", timeout=10)
        r.raise_for_status()
        return r.json()
    except Exception as e:
        return {"error": str(e)}


def get_health():
    try:
        r = requests.get(f"{API_BASE_URL}/health", timeout=5)
        r.raise_for_status()
        return r.json()
    except Exception as e:
        return {"error": str(e)}


def load_historical_data():
    """Load data historis dari CSV yang dihasilkan notebook."""
    csv_path = os.path.join(
        os.path.dirname(__file__), "..", "data",
        "weekly_demand_per_kategori_FIXED.csv",
    )
    if not os.path.exists(csv_path):
        return None
    return pd.read_csv(csv_path, parse_dates=["TGL"])