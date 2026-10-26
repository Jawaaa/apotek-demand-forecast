# Apotek Demand Forecast

**Sistem prediksi kebutuhan obat mingguan dengan LSTM** — aplikasi end-to-end (FastAPI + SQLite + Streamlit) untuk memprediksi permintaan obat per kategori dan memberi rekomendasi restock.

## Latar Belakang
Apotek berisiko mengalami *stockout* (penjualan hilang) dan *overstock* (modal mati, obat kedaluwarsa). Sistem ini menjawab: **"Obat apa yang harus di-restock minggu depan, dan berapa banyak?"**

## Dataset
- Sumber: transaksi apotek Indonesia (`sales.sql`), periode 2015-01-01 s/d 2015-12-31
- Setelah cleaning: 410,536 baris transaksi, 2,162 obat unik
- Dikelompokkan ke 12 kategori terapi; agregasi **mingguan (Senin-Minggu), dijumlahkan** — 53 minggu per kategori, tidak ada minggu yang di-drop
- Minggu parsial di ujung rentang data (2 minggu) tetap dipakai dan diberi penanda

## Metodologi
Split kronologis: Train -> Validation (8 minggu) -> Test (13 minggu). Hyperparameter tuning (grid search 24 konfigurasi) memakai data validation; data test hanya untuk pelaporan.

Konfigurasi LSTM terbaik: `{'lookback': 8, 'units': 32, 'lr': 0.005, 'dropout': 0.2}`

## Hasil Model (data test)
| Model | RMSE | MAPE (%) |
|---|---|---|
| Naive (minggu lalu) | 1090.30 | 16.44 |
| Moving Average (window=2, awal) | 903.80 | 14.40 |
| Moving Average (window=4, terbaik) | 910.20 | 13.80 |
| Linear Regression (lag=2) | 1079.30 | 13.79 |
| LSTM sebelum tuning | 856.40 | 13.12 |
| LSTM setelah tuning | 1168.60 | 15.92 |


Analisis selisih LSTM vs Moving Average: selisih -2.12 poin MAPE (CI 95% bootstrap [-3.74, -0.21]), LSTM lebih baik di 5/12 kategori. Autokorelasi antar-minggu rata-rata 0.45; acuan error 'level sempurna' (prediksi konstan) adalah MAPE 11.6%, dan data hanya ~1 tahun.

## Fitur Utama
| Fitur | Deskripsi |
|---|---|
| Beranda | Ringkasan restock semua kategori |
| Prediksi | Prediksi per kategori dengan LSTM |
| Performa | KPI model dan perbandingan dengan baseline |
| Stok | Upload data penjualan + analisis stockout |
| Riwayat | Log semua prediksi dari database |

## Tech Stack
TensorFlow/Keras - FastAPI + Uvicorn - SQLite + SQLAlchemy - Streamlit + Plotly - Pytest - GitHub Actions - Python 3.11

## Cara Menjalankan
```bash
git clone https://github.com/Jawaaa/apotek-demand-forecast.git
cd apotek-demand-forecast
python -m venv venv
venv\Scripts\activate        # Windows  (Mac/Linux: source venv/bin/activate)
pip install -r requirements.txt
uvicorn api.main:app --reload --port 8000      # Terminal 1
streamlit run ui/app.py                         # Terminal 2
pytest tests/test_api.py -v                     # Testing
```

## API
| Method | Endpoint | Deskripsi |
|---|---|---|
| GET | /health | Cek status API |
| GET | /categories | Daftar 12 kategori |
| POST | /predict | Prediksi + rekomendasi restock |
| GET | /history | Riwayat prediksi |

## Limitasi
1. Data historis hanya 53 minggu (1 tahun)
2. MAPE mengasumsikan biaya error simetris
3. Klasifikasi kategori berbasis keyword
4. Belum terintegrasi dengan inventori aktual

## Rekomendasi ke Depan
Tambah data 2-3 tahun dan fitur kalender, integrasi inventori, autentikasi, deploy cloud, Docker, monitoring.

## Author
**Zahwa Rizzi Ani** — Final Project Bootcamp Data Science & AI Machine Learning (Dibimbing), Batch 42
