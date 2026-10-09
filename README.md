## 💊 Apotek Demand Forecast :
**Sistem Prediksi Kebutuhan Obat dengan LSTM**

Aplikasi end-to-end untuk memprediksi permintaan obat mingguan per kategori menggunakan Deep Learning (LSTM), dengan REST API, database, dan dashboard interaktif berbasis Streamlit.

---

## 📌 Latar Belakang

Apotek sering mengalami:
- 🔴 Stockout — stok habis, pelanggan kecewa, kehilangan penjualan
- 🟡 Overstock — modal mati, obat kadaluarsa

Sistem ini menjawab pertanyaan bisnis: **"Obat apa yang harus di-restock minggu depan, dan berapa banyak?"**

---

## 🎯 Fitur Utama

| Fitur | Deskripsi |
|-------|-----------|
| 🏠 Dashboard Keputusan | Ringkasan restock semua kategori sekaligus |
| 🔮 Prediksi Real-time | Prediksi per kategori dengan LSTM |
| 📊 Performa Model | KPI bisnis, akurasi, dan dampak finansial |
| 📦 Manajemen Stok | Upload data penjualan + analisis stockout otomatis |
| 📤 Upload Data | Upload CSV penjualan eksternal |
| 📜 Riwayat | Log semua prediksi dari database |

---

## 🛠️ Tech Stack

| Komponen | Teknologi |
|----------|-----------|
| Deep Learning | TensorFlow 2.15 + Keras 3 |
| Backend API | FastAPI 0.110 + Uvicorn |
| Database | SQLite + SQLAlchemy |
| Frontend UI | Streamlit 1.31 + Plotly |
| Testing | Pytest 8.0 |
| CI/CD | GitHub Actions |
| Bahasa | Python 3.11 |

---

## 📁 Struktur Project

<img width="581" height="416" alt="image" src="https://github.com/user-attachments/assets/163cafde-fb6f-4182-b757-00a085c02428" />


---

## 🚀 Cara Menjalankan

### Prasyarat
- Python 3.10 atau 3.11
- pip
- Git

### 1. Clone Repository

git clone https://github.com/USERNAME/apotek-demand-forecast.git
cd apotek-demand-forecast

### 2. Buat Virtual Environment

Windows:
python -m venv venv
venv\\Scripts\\activate

Mac/Linux:
python3 -m venv venv
source venv/bin/activate

### 3. Install Dependencies

pip install -r requirements.txt

### 4. Jalankan API (Terminal 1)

uvicorn api.main:app --reload --port 8000

Buka http://127.0.0.1:8000/docs

### 5. Jalankan Streamlit UI (Terminal 2)

streamlit run ui/app.py

Buka http://localhost:8501

---

## 🧪 Testing

pytest tests/test_api.py -v

Hasil: 12 tests passed ✅

---

## 🔌 API Endpoints

| Method | Endpoint | Deskripsi |
|--------|----------|-----------|
| GET | / | Welcome page |
| GET | /health | Cek status API |
| GET | /categories | Daftar 12 kategori |
| GET | /categories/{nama} | Info kategori |
| POST | /predict | Prediksi + rekomendasi |
| GET | /history | Riwayat prediksi |

### Contoh Request

curl -X POST http://127.0.0.1:8000/predict -H "Content-Type: application/json" -d "{\\"kategori\\": \\"Alergi\\", \\"buffer_pct\\": 20}"

### Contoh Response

{
  "kategori": "Alergi",
  "predicted_qty": 1066.9,
  "recommendation_restock": 1280.3,
  "buffer_pct": 20,
  "last_date": "2015-12-28"
}

---

## 🧠 Sistem Kerja

1. User pilih kategori di Streamlit
2. Streamlit kirim request ke API /predict
3. API pilih model LSTM sesuai kategori
4. Model prediksi demand minggu depan
5. API simpan hasil ke database
6. Streamlit tampilkan hasil ke user

Arsitektur:

Streamlit UI -> FastAPI -> LSTM Models (12) -> SQLite DB

---

## 📊 Hasil Model

| Model | MAPE (%) | Keterangan |
|-------|----------|------------|
| LSTM per Kategori | 13.3 | Model utama |
| Moving Average | 13.9 | Baseline tradisional |
| Linear Regression | 21.8 | Baseline statistik |

Kesimpulan: LSTM mengalahkan 2 baseline meskipun data hanya 9 minggu.

---

## 📦 Dataset

- Sumber: Database apotek (sales.sql)
- Periode: Oktober - Desember 2015
- Total transaksi: 55.000 baris
- Kategori: 12 kategori obat
- Frekuensi: Mingguan

---

## ⚠️ Limitasi

1. Data historis hanya 9 minggu
2. MAPE mengasumsikan biaya error simetris
3. Klasifikasi berbasis keyword
4. Belum integrasi dengan inventori aktual

---

## 🎯 Rekomendasi Ke Depan

- Tambah data historis 1-2 tahun
- Integrasi dengan sistem inventori
- Authentication & authorization
- Deploy ke cloud
- Monitoring (Prometheus + Grafana)
- Containerization (Docker)

---

## 👤 Author

**Zahwa Rizzi Ani**
Data Science & AI Machine Learning — Batch 42

---

## 📄 License

Project ini dibuat untuk keperluan Final Project Bootcamp Data Science & AI Machine Learning Batch 42.
"""

