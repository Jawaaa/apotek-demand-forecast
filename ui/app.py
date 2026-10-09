"""
Apotek Demand Forecast — Business Analytics Dashboard
Cara run:
    streamlit run ui/app.py
"""
import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
import requests
import os

# ============================================================
# KONFIGURASI
# ============================================================
API_BASE_URL = "http://127.0.0.1:8000"
DATA_DIR = os.path.join(os.path.dirname(__file__), "..", "data")


# ============================================================
# HELPER FUNCTIONS
# ============================================================
def get_categories():
    try:
        r = requests.get(f"{API_BASE_URL}/categories", timeout=10)
        r.raise_for_status()
        return r.json()
    except Exception as e:
        return {"error": str(e)}


def predict(kategori, buffer_pct=20.0):
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


def get_history(limit=20):
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
    csv_path = os.path.join(DATA_DIR, "weekly_demand_per_kategori.csv")
    if not os.path.exists(csv_path):
        return None
    try:
        return pd.read_csv(csv_path, parse_dates=["TGL"])
    except Exception:
        return None


def load_performance_data():
    csv_path = os.path.join(DATA_DIR, "model_performance.csv")
    if not os.path.exists(csv_path):
        return None
    try:
        return pd.read_csv(csv_path)
    except Exception:
        return None


def get_all_recommendations(categories, buffer_pct=20.0):
    results = []
    for cat in categories:
        res = predict(cat, buffer_pct)
        if "error" not in res:
            results.append(res)
    return pd.DataFrame(results)


# ============================================================
# KONFIGURASI HALAMAN
# ============================================================
st.set_page_config(
    page_title="Apotek Demand Forecast",
    page_icon="💊",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ============================================================
# CUSTOM CSS
# ============================================================
st.markdown("""
<style>
    .main-title { font-size: 2.2rem; font-weight: 700; color: #0d4e8c; margin-bottom: 0.2rem; }
    .subtitle { font-size: 1rem; color: #666; margin-bottom: 1.5rem; }
    .kpi-card {
        background: linear-gradient(135deg, #0d4e8c 0%, #1f77b4 100%);
        color: white; padding: 1.3rem; border-radius: 0.8rem;
        text-align: center; box-shadow: 0 4px 12px rgba(0,0,0,0.1);
    }
    .kpi-value { font-size: 2rem; font-weight: bold; margin: 0.3rem 0; }
    .kpi-label { font-size: 0.85rem; opacity: 0.9; text-transform: uppercase; letter-spacing: 0.5px; }
    .stButton>button { background-color: #0d4e8c; color: white; font-weight: 600; border-radius: 0.5rem; }
    .stButton>button:hover { background-color: #1f77b4; }
    .big-decision {
        background: linear-gradient(135deg, #2a9d8f 0%, #264653 100%);
        color: white; padding: 1.5rem; border-radius: 1rem; text-align: center; margin: 1rem 0;
    }
    .big-decision-value { font-size: 2.8rem; font-weight: bold; margin: 0.5rem 0; }
</style>
""", unsafe_allow_html=True)


# ============================================================
# HEADER
# ============================================================
st.markdown('<div class="main-title">💊 Sistem Prediksi Kebutuhan Obat</div>', unsafe_allow_html=True)
st.markdown('<div class="subtitle">Bantu apotek putuskan: <b>obat apa</b>, <b>berapa banyak</b>, <b>kapan</b> harus restock.</div>', unsafe_allow_html=True)


# ============================================================
# SIDEBAR
# ============================================================
with st.sidebar:
    st.markdown("### 💊 Menu")
    page = st.radio(
        "Pilih Halaman:",
        [
            "🏠 Beranda",
            "🔮 Analisis Prediksi",
            "📊 Performa Model",
            "📦 Manajemen Stok",
            "📜 Riwayat & Laporan",
        ],
        label_visibility="collapsed",
    )
    st.divider()

    st.markdown("### ⚙️ Pengaturan")
    buffer_pct = st.slider(
        "Buffer Keamanan Stok (%)",
        0, 50, 20, 5,
        help="Cadangan stok untuk antisipasi lonjakan permintaan",
    )

    st.divider()
    health = get_health()
    if "error" in health:
        st.error("⚠️ Sistem tidak aktif")
        st.caption("Hubungi tim IT untuk mengaktifkan sistem.")
    else:
        st.success("✅ Sistem Aktif")
        st.caption(f"{health.get('models_loaded', 0)} kategori siap diprediksi")


# ============================================================
# HALAMAN 1: BERANDA
# ============================================================
if page == "🏠 Beranda":
    st.header("🏠 Ringkasan Keputusan Minggu Ini")
    st.caption("Lihat semua kategori sekaligus — langsung tahu apa yang perlu di-restock")

    categories = get_categories()
    if "error" in categories:
        st.error("⚠️ Sistem tidak aktif. Hubungi tim IT.")
        st.stop()

    df_hist = load_historical_data()

    col1, col2 = st.columns([4, 1])
    with col2:
        if st.button("🔄 Refresh Prediksi", use_container_width=True):
            st.rerun()

    with st.spinner("Menghitung prediksi untuk semua kategori..."):
        df_recs = get_all_recommendations(categories, buffer_pct)

    if df_recs.empty:
        st.warning("Belum ada prediksi. Coba refresh.")
        st.stop()

    col1, col2, col3 = st.columns(3)
    total_demand = df_recs["predicted_qty"].sum()
    total_restock = df_recs["recommendation_restock"].sum()

    with col1:
        st.markdown(f"""
        <div class="kpi-card">
            <div class="kpi-label">Total Kebutuhan Minggu Depan</div>
            <div class="kpi-value">{total_demand:,.0f}</div>
            <div class="kpi-label">unit obat</div>
        </div>
        """, unsafe_allow_html=True)
    with col2:
        st.markdown(f"""
        <div class="kpi-card">
            <div class="kpi-label">Total yang Perlu Distok</div>
            <div class="kpi-value">{total_restock:,.0f}</div>
            <div class="kpi-label">unit (buffer {buffer_pct}%)</div>
        </div>
        """, unsafe_allow_html=True)
    with col3:
        st.markdown(f"""
        <div class="kpi-card">
            <div class="kpi-label">Kategori Dipantau</div>
            <div class="kpi-value">{len(df_recs)}</div>
            <div class="kpi-label">kategori obat</div>
        </div>
        """, unsafe_allow_html=True)

    st.divider()
    st.subheader("📋 Daftar Keputusan Restock")
    st.caption("Diurutkan dari yang paling banyak dibutuhkan")

    df_decision = df_recs.copy().rename(columns={
        "kategori": "Kategori Obat",
        "predicted_qty": "Prediksi Minggu Depan",
        "recommendation_restock": "Rekomendasi Restock",
        "last_date": "Data Terakhir",
    })

    if df_hist is not None:
        avg_per_cat = df_hist.groupby("KATEGORI")["QTY_SOLD"].mean().to_dict()
        df_decision["Rata-rata Historis"] = df_decision["Kategori Obat"].map(avg_per_cat).round(0)

        def get_urgency(row):
            pred = row["Prediksi Minggu Depan"]
            avg = row.get("Rata-rata Historis", 0)
            if pd.isna(avg) or avg == 0:
                return "🟢 Normal"
            ratio = pred / avg
            if ratio > 1.15:
                return "🔴 Tinggi"
            elif ratio > 0.9:
                return "🟡 Sedang"
            return "🟢 Normal"

        df_decision["Tingkat Kebutuhan"] = df_decision.apply(get_urgency, axis=1)
        df_decision = df_decision[[
            "Kategori Obat", "Tingkat Kebutuhan", "Rata-rata Historis",
            "Prediksi Minggu Depan", "Rekomendasi Restock",
        ]].sort_values("Rekomendasi Restock", ascending=False)

    st.dataframe(df_decision, use_container_width=True, hide_index=True)

    st.divider()
    st.subheader("📊 Perbandingan Kebutuhan per Kategori")
    fig = go.Figure()
    fig.add_trace(go.Bar(
        x=df_recs["kategori"], y=df_recs["predicted_qty"],
        name="Prediksi Kebutuhan", marker_color="#1f77b4",
    ))
    fig.add_trace(go.Bar(
        x=df_recs["kategori"], y=df_recs["recommendation_restock"],
        name=f"Rekomendasi Restock (+{buffer_pct}%)", marker_color="#2a9d8f",
    ))
    fig.update_layout(
        barmode="group", xaxis_title="", yaxis_title="Jumlah Unit",
        height=450, hovermode="x unified",
    )
    st.plotly_chart(fig, use_container_width=True)

    st.divider()
    csv = df_decision.to_csv(index=False).encode("utf-8")
    st.download_button(
        "📥 Download Daftar Restock (CSV)",
        data=csv,
        file_name=f"rekomendasi_restock_{datetime.now().strftime('%Y%m%d')}.csv",
        mime="text/csv",
        use_container_width=True,
    )


# ============================================================
# HALAMAN 2: ANALISIS PREDIKSI
# ============================================================
elif page == "🔮 Analisis Prediksi":
    st.header("🔮 Analisis Prediksi per Kategori")
    st.caption("Prediksi detail + rekomendasi tindakan untuk 1 kategori")

    categories = get_categories()
    if "error" in categories:
        st.error("⚠️ Sistem tidak aktif")
        st.stop()

    col1, col2 = st.columns([2, 1])
    with col1:
        kategori = st.selectbox("Pilih Kategori Obat:", categories)

    if st.button("🔮 Analisis Sekarang", use_container_width=True):
        with st.spinner("Menganalisis..."):
            result = predict(kategori, buffer_pct)

        if "error" in result:
            st.error(f"Error: {result['error']}")
        else:
            st.divider()
            st.markdown(f"""
            <div class="big-decision">
                <div style="font-size: 1rem; opacity: 0.9;">KEPUTUSAN UNTUK KATEGORI {kategori.upper()}</div>
                <div class="big-decision-value">{result['recommendation_restock']:,.0f} unit</div>
                <div style="font-size: 1rem; opacity: 0.9;">perlu di-restock minggu depan</div>
            </div>
            """, unsafe_allow_html=True)

            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("📦 Prediksi Kebutuhan", f"{result['predicted_qty']:,.0f} unit",
                          help="Perkiraan jumlah yang akan terjual minggu depan")
            with col2:
                st.metric("🛒 Rekomendasi Restock", f"{result['recommendation_restock']:,.0f} unit",
                          delta=f"+{buffer_pct}% buffer",
                          help="Jumlah yang perlu disiapkan")
            with col3:
                st.metric("📅 Berdasarkan Data", result["last_date"])

            st.divider()
            st.subheader("💡 Interpretasi & Rekomendasi")
            st.info(
                f"**Untuk kategori {kategori}:**\n\n"
                f"📌 Diperkirakan **{result['predicted_qty']:,.0f} unit** akan terjual minggu depan.\n\n"
                f"✅ Disarankan restock **{result['recommendation_restock']:,.0f} unit** "
                f"(sudah termasuk buffer keamanan {buffer_pct}%).\n\n"
                f"🎯 **Tindakan:** Siapkan pesanan ke supplier untuk kategori ini sebelum minggu depan."
            )

            st.subheader("📈 Tren Historis + Prediksi")
            df_hist = load_historical_data()
            if df_hist is not None:
                df_cat = df_hist[df_hist["KATEGORI"] == kategori].sort_values("TGL")
                fig = go.Figure()
                fig.add_trace(go.Scatter(
                    x=df_cat["TGL"], y=df_cat["QTY_SOLD"],
                    mode="lines+markers", name="Penjualan Historis",
                    line=dict(color="steelblue", width=2),
                ))
                next_week = df_cat["TGL"].max() + timedelta(weeks=1)
                fig.add_trace(go.Scatter(
                    x=[next_week], y=[result["predicted_qty"]],
                    mode="markers", name="Prediksi Minggu Depan",
                    marker=dict(color="darkorange", size=20, symbol="star"),
                ))
                avg_val = df_cat["QTY_SOLD"].mean()
                fig.add_hline(y=avg_val, line_dash="dash", line_color="gray",
                              annotation_text=f"Rata-rata: {avg_val:.0f}")
                fig.update_layout(xaxis_title="Minggu", yaxis_title="Jumlah Terjual (unit)",
                                  height=420, hovermode="x unified")
                st.plotly_chart(fig, use_container_width=True)


# ============================================================
# HALAMAN 3: PERFORMA MODEL
# ============================================================
elif page == "📊 Performa Model":
    st.header("📊 Performa Model — Perspektif Bisnis")
    st.caption("Seberapa akurat sistem prediksi kita, dan apa dampaknya bagi apotek?")

    df_perf = load_performance_data()
    if df_perf is None:
        st.warning("⚠️ File `data/model_performance.csv` tidak ditemukan.")
        st.info("Hubungi tim data untuk mendapatkan file performa model.")
        st.stop()

    # ===== ASUMSI BISNIS =====
    with st.expander("⚙️ Asumsi Bisnis (klik untuk ubah)", expanded=False):
        col1, col2, col3 = st.columns(3)
        with col1:
            harga_per_unit = st.number_input(
                "Harga rata-rata per unit (Rp)",
                min_value=1000, max_value=1000000, value=50000, step=5000,
                help="Harga jual rata-rata obat per unit",
            )
        with col2:
            cost_overstock_pct = st.slider(
                "Biaya overstock (% dari nilai)",
                1, 50, 15, 1,
                help="Persentase modal yang 'mati' karena stok berlebih",
            )
        with col3:
            cost_stockout_pct = st.slider(
                "Biaya stockout (% dari nilai)",
                1, 50, 25, 1,
                help="Kerugian karena kehilangan penjualan",
            )

    st.divider()

    # ===== KPI TEKNIS + BISNIS =====
    st.subheader("🎯 Ringkasan Performa & Dampak Bisnis")

    avg_mape = df_perf.groupby("Model")["MAPE"].mean().round(2)
    lstm_mape = avg_mape.get("LSTM per Kategori", 0)
    lr_mape = avg_mape.get("Linear Regression", 1)
    ma_mape = avg_mape.get("Moving Average", 1)

    improvement_vs_lr = ((lr_mape - lstm_mape) / lr_mape * 100) if lr_mape > 0 else 0

    df_hist = load_historical_data()
    if df_hist is not None:
        total_weekly_demand = df_hist.groupby("TGL")["QTY_SOLD"].sum().mean()
        annual_demand = total_weekly_demand * 52
    else:
        annual_demand = 50000

    error_reduction = improvement_vs_lr / 100
    potential_savings = annual_demand * harga_per_unit * error_reduction * (
        (cost_overstock_pct + cost_stockout_pct) / 200
    )

    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.markdown(f"""
        <div class="kpi-card">
            <div class="kpi-label">Akurasi Sistem AI</div>
            <div class="kpi-value">{100-lstm_mape:.1f}%</div>
            <div class="kpi-label">rata-rata semua kategori</div>
        </div>
        """, unsafe_allow_html=True)
    with col2:
        st.markdown(f"""
        <div class="kpi-card">
            <div class="kpi-label">Service Level</div>
            <div class="kpi-value">{100-lstm_mape:.1f}%</div>
            <div class="kpi-label">perkiraan permintaan terpenuhi</div>
        </div>
        """, unsafe_allow_html=True)
    with col3:
        st.markdown(f"""
        <div class="kpi-card">
            <div class="kpi-label">Lebih Akurat vs Metode Lama</div>
            <div class="kpi-value">{improvement_vs_lr:.1f}%</div>
            <div class="kpi-label">dibanding Linear Regression</div>
        </div>
        """, unsafe_allow_html=True)
    with col4:
        st.markdown(f"""
        <div class="kpi-card">
            <div class="kpi-label">Estimasi Hemat / Tahun</div>
            <div class="kpi-value">Rp {potential_savings/1e6:.1f} Jt</div>
            <div class="kpi-label">dari optimasi stok</div>
        </div>
        """, unsafe_allow_html=True)

    st.info(f"""
    💡 **Cara Baca KPI di Atas:**

    - **Akurasi {100-lstm_mape:.1f}%** → prediksi rata-rata meleset **{lstm_mape:.1f}%**
    - **Service Level {100-lstm_mape:.1f}%** → perkiraan permintaan yang bisa dipenuhi
    - **Improvement {improvement_vs_lr:.1f}%** → sistem AI lebih baik dari Linear Regression
    - **Hemat Rp {potential_savings/1e6:.1f} Juta/tahun** → estimasi dari pengurangan error

    ⚠️ *Angka finansial adalah estimasi berdasarkan asumsi di panel "Asumsi Bisnis".*
    """)

    st.divider()

    # ===== PERBANDINGAN MODEL =====
    st.subheader("🥇 Perbandingan 3 Metode Prediksi")
    st.caption("Makin rendah MAPE, makin akurat prediksinya")

    colors = {"Moving Average": "#94a3b8", "Linear Regression": "#f4a261", "LSTM per Kategori": "#2a9d8f"}
    fig_compare = go.Figure()
    for model in avg_mape.index:
        fig_compare.add_trace(go.Bar(
            x=[model], y=[avg_mape[model]], name=model,
            marker_color=colors.get(model, "#1f77b4"),
            text=[f"{avg_mape[model]:.1f}%"], textposition="outside",
        ))
    fig_compare.update_layout(
        yaxis_title="MAPE (%) — Makin Kecil Makin Akurat",
        xaxis_title="", height=380, showlegend=False,
        yaxis_range=[0, max(avg_mape.values) * 1.2],
    )
    st.plotly_chart(fig_compare, use_container_width=True)

    best_model = avg_mape.idxmin()
    st.success(f"""
    ✅ **Model Terbaik:** {best_model} (MAPE rata-rata **{avg_mape[best_model]:.1f}%**)

    Sistem AI (LSTM) kami **{improvement_vs_lr:.1f}% lebih akurat** dibanding Linear Regression
    dan **kompetitif** dengan Moving Average.
    """)

    st.divider()

    # ===== AKURASI PER KATEGORI =====
    st.subheader("🔥 Akurasi per Kategori Obat")
    st.caption("Kategori mana yang paling akurat diprediksi?")

    view_mode = st.radio(
        "Pilih Tampilan:",
        ["📊 Bar Chart", "🔥 Heatmap"],
        horizontal=True,
        label_visibility="collapsed",
    )

    try:
        if view_mode == "📊 Bar Chart":
            fig_heat = px.bar(
                df_perf, x="Kategori", y="MAPE", color="Model", barmode="group",
                title="Akurasi per Kategori (MAPE) — makin rendah makin baik",
                color_discrete_map=colors,
            )
            fig_heat.update_layout(height=500, xaxis_tickangle=-45)
            st.plotly_chart(fig_heat, use_container_width=True)
        else:
            pivot = df_perf.pivot_table(index="Kategori", columns="Model", values="MAPE", aggfunc="mean")
            if not pivot.empty:
                fig_heat = go.Figure(data=go.Heatmap(
                    z=pivot.values, x=pivot.columns.tolist(), y=pivot.index.tolist(),
                    colorscale=[[0, "#2a9d8f"], [0.5, "#f4a261"], [1, "#e63946"]],
                    text=pivot.values, texttemplate="%{text:.1f}",
                    textfont={"size": 11}, colorbar=dict(title="MAPE (%)"),
                ))
                fig_heat.update_layout(height=500, xaxis_title="Model", yaxis_title="Kategori")
                st.plotly_chart(fig_heat, use_container_width=True)
    except Exception as e:
        st.error(f"Gagal render grafik: {e}")

    lstm_only = df_perf[df_perf["Model"] == "LSTM per Kategori"].sort_values("MAPE")
    if not lstm_only.empty:
        best_cat = lstm_only.iloc[0]
        worst_cat = lstm_only.iloc[-1]
        col1, col2 = st.columns(2)
        with col1:
            st.success(f"""
            ✅ **Paling Akurat:** {best_cat['Kategori']}
            MAPE hanya **{best_cat['MAPE']:.1f}%** — bisa diandalkan
            """)
        with col2:
            st.warning(f"""
            ⚠️ **Perlu Perhatian:** {worst_cat['Kategori']}
            MAPE **{worst_cat['MAPE']:.1f}%** — perlu verifikasi manual
            """)

    st.divider()

    # ===== TABEL DETAIL =====
    st.subheader("📋 Tabel Detail Akurasi per Kategori")
    detail = df_perf.pivot_table(index="Kategori", columns="Model", values="MAPE").round(2)
    if "Linear Regression" in detail.columns and "LSTM per Kategori" in detail.columns:
        detail["Selisih LSTM vs LR"] = (detail["Linear Regression"] - detail["LSTM per Kategori"]).round(2)
    detail = detail.sort_values("LSTM per Kategori")
    st.dataframe(detail, use_container_width=True)

    st.divider()

    # ===== EXPORT =====
    csv = df_perf.to_csv(index=False).encode("utf-8")
    st.download_button(
        "📄 Download Laporan Performa (CSV)", data=csv,
        file_name=f"laporan_performa_model_{datetime.now().strftime('%Y%m%d')}.csv",
        mime="text/csv", use_container_width=True,
    )


# ============================================================
# HALAMAN 4: MANAJEMEN STOK & STOCKOUT ANALYSIS (BARU!)
# ============================================================
# ============================================================
# HALAMAN 4: MANAJEMEN STOK & STOCKOUT ANALYSIS (AUTO)
# ============================================================
elif page == "📦 Manajemen Stok":
    st.header("📦 Manajemen Stok & Analisis Stockout")
    st.caption("Upload data penjualan dari sistem eksternal → sistem otomatis prediksi kebutuhan minggu depan")

    # ===== STEP 1: UPLOAD =====
    st.subheader("📤 Step 1: Upload Data Penjualan")
    st.caption("Data penjualan terbaru dari sistem POS apotek (CSV: TGL, KATEGORI, QTY_SOLD)")

    uploaded_file = st.file_uploader(
        "Upload file CSV:", type=["csv"], key="stock_file_uploader",
    )

    if uploaded_file is None:
        st.info("💡 Belum ada file di-upload. Upload CSV untuk memulai analisis.")
        st.markdown("""
        **Belum punya file?** Download template dulu:
        """)
        template_df = pd.DataFrame({
            "TGL": ["2015-12-21", "2015-12-21", "2015-12-21", "2015-12-28", "2015-12-28", "2015-12-28"],
            "KATEGORI": ["Alergi", "Antibiotik", "Diabetes", "Alergi", "Antibiotik", "Diabetes"],
            "QTY_SOLD": [1150, 3300, 9200, 1100, 3200, 9500],
        })
        st.download_button(
            "📄 Download Template CSV",
            data=template_df.to_csv(index=False).encode("utf-8"),
            file_name="template_penjualan.csv",
            mime="text/csv",
        )
        st.stop()

    # ===== STEP 2: PARSE & VALIDASI =====
    try:
        sales_df = pd.read_csv(uploaded_file)
        if not {"TGL", "KATEGORI", "QTY_SOLD"}.issubset(sales_df.columns):
            st.error(f"❌ Kolom tidak lengkap. Butuh: TGL, KATEGORI, QTY_SOLD")
            st.write("Kolom yang ada:", list(sales_df.columns))
            st.stop()
    except Exception as e:
        st.error(f"❌ Gagal baca file: {e}")
        st.stop()

    # Bersihkan data
    sales_df["TGL"] = pd.to_datetime(sales_df["TGL"], errors="coerce")
    sales_df["QTY_SOLD"] = pd.to_numeric(sales_df["QTY_SOLD"], errors="coerce")
    sales_df = sales_df.dropna()

    st.success(f"✅ Data berhasil dibaca: {len(sales_df)} baris, "
               f"{sales_df['KATEGORI'].nunique()} kategori, "
               f"periode {sales_df['TGL'].min().date()} s/d {sales_df['TGL'].max().date()}")

    with st.expander("👁️ Preview Data"):
        st.dataframe(sales_df, use_container_width=True, hide_index=True)

    st.divider()

    # ===== STEP 3: HITUNG STOK SAAT INI DARI DATA =====
    # Stok "saat ini" dihitung dari penjualan terakhir (minggu terakhir di data)
    # Asumsi: apotek punya stok = penjualan minggu terakhir × rasio (default 0.85)
    st.subheader("⚙️ Step 2: Rasio Stok Saat Ini")

    st.markdown("""
    Sistem akan **otomatis menghitung stok saat ini** berdasarkan penjualan minggu terakhir.
    
    **Formula:** `Stok Saat Ini = Penjualan Minggu Terakhir × Rasio`
    """)

    col1, col2 = st.columns([2, 1])
    with col1:
        rasio = st.slider(
            "Rasio Stok terhadap Penjualan Minggu Terakhir",
            min_value=0.3, max_value=1.5, value=0.85, step=0.05,
            help="Rasio < 1 = stok lebih sedikit dari penjualan (berpotensi stockout). Rasio > 1 = stok berlebih.",
        )
    with col2:
        st.metric("Rasio", f"{rasio:.0%}")

    st.info(f"""
    💡 **Contoh:** Kalau penjualan minggu terakhir kategori Alergi = 1.000 unit,
    maka stok saat ini otomatis dihitung **{rasio:.0%} × 1.000 = {int(1000 * rasio)} unit**.

    Ubah slider untuk simulasi skenario berbeda (misal 0.5 = stok cuma 50% dari penjualan).
    """)

    st.divider()

    # ===== STEP 4: ANALISIS OTOMATIS =====
    st.subheader("🔍 Step 3: Analisis Stockout")

    # Ambil kategori dari data yang diupload
    kategori_di_file = sorted(sales_df["KATEGORI"].unique())

    # Cek kategori mana yang ada di sistem model
    all_categories = get_categories()
    if "error" in all_categories:
        st.error("⚠️ API tidak aktif. Jalankan uvicorn terlebih dahulu.")
        st.stop()

    kategori_valid = [c for c in kategori_di_file if c in all_categories]
    kategori_tidak_ada = [c for c in kategori_di_file if c not in all_categories]

    if kategori_tidak_ada:
        st.warning(f"⚠️ Kategori berikut tidak ada di model, akan di-skip: {', '.join(kategori_tidak_ada)}")

    if not kategori_valid:
        st.error("❌ Tidak ada kategori yang valid untuk dianalisis.")
        st.stop()

    # Tombol analisis
    if st.button("📊 Analisis Sekarang", use_container_width=True, type="primary"):

        with st.spinner(f"Memprediksi {len(kategori_valid)} kategori..."):
            df_pred = get_all_recommendations(kategori_valid, buffer_pct)

            if df_pred.empty:
                st.error("Gagal ambil prediksi. Cek API.")
                st.stop()

            # Hitung stok saat ini = penjualan minggu terakhir × rasio
            # Ambil penjualan minggu terakhir per kategori dari data yang diupload
            last_week_per_cat = {}
            for cat in kategori_valid:
                sub_cat = sales_df[sales_df["KATEGORI"] == cat].sort_values("TGL")
                if not sub_cat.empty:
                    # Ambil baris dengan TGL terakhir
                    last_date = sub_cat["TGL"].max()
                    last_qty = sub_cat[sub_cat["TGL"] == last_date]["QTY_SOLD"].sum()
                    last_week_per_cat[cat] = last_qty

            df_pred["Penjualan Minggu Lalu"] = df_pred["kategori"].map(last_week_per_cat).fillna(0).astype(int)
            df_pred["Stok Saat Ini"] = (df_pred["Penjualan Minggu Lalu"] * rasio).round(0).astype(int)

            # Hitung stockout
            df_pred["Risiko Stockout"] = (df_pred["predicted_qty"] - df_pred["Stok Saat Ini"]).clip(lower=0)
            df_pred["Restock Diperlukan"] = (df_pred["Risiko Stockout"] * (1 + buffer_pct / 100)).round(0).astype(int)

            # Klasifikasi urgensi
            def klasifikasi_urgensi(row):
                risk = row["Risiko Stockout"]
                stok = row["Stok Saat Ini"]
                if risk <= 0:
                    return "🟢 Aman"
                rasio_risk = risk / max(stok, 1)
                if rasio_risk > 0.3:
                    return "🔴 Kritis"
                elif rasio_risk > 0.1:
                    return "🟡 Perhatian"
                return "🟢 Aman"

            df_pred["Urgensi"] = df_pred.apply(klasifikasi_urgensi, axis=1)

            df_pred = df_pred.rename(columns={
                "kategori": "Kategori",
                "predicted_qty": "Prediksi Minggu Depan",
            })
            df_pred = df_pred[[
                "Kategori", "Urgensi", "Penjualan Minggu Lalu",
                "Stok Saat Ini", "Prediksi Minggu Depan",
                "Risiko Stockout", "Restock Diperlukan"
            ]].sort_values("Risiko Stockout", ascending=False)

            # ===== KPI =====
            st.divider()
            st.subheader("📊 Ringkasan Analisis")

            n_kritis = (df_pred["Urgensi"] == "🔴 Kritis").sum()
            n_perhatian = (df_pred["Urgensi"] == "🟡 Perhatian").sum()
            total_restock = df_pred["Restock Diperlukan"].sum()
            total_stockout = df_pred["Risiko Stockout"].sum()

            col1, col2, col3, col4 = st.columns(4)
            with col1:
                st.markdown(f"""
                <div class="kpi-card" style="background: linear-gradient(135deg, #e63946 0%, #a4161a 100%);">
                    <div class="kpi-label">Kategori Kritis</div>
                    <div class="kpi-value">{n_kritis}</div>
                    <div class="kpi-label">risiko stockout tinggi</div>
                </div>
                """, unsafe_allow_html=True)
            with col2:
                st.markdown(f"""
                <div class="kpi-card" style="background: linear-gradient(135deg, #f4a261 0%, #e76f51 100%);">
                    <div class="kpi-label">Perlu Perhatian</div>
                    <div class="kpi-value">{n_perhatian}</div>
                    <div class="kpi-label">kategori</div>
                </div>
                """, unsafe_allow_html=True)
            with col3:
                st.markdown(f"""
                <div class="kpi-card" style="background: linear-gradient(135deg, #2a9d8f 0%, #264653 100%);">
                    <div class="kpi-label">Total Restock Dibutuhkan</div>
                    <div class="kpi-value">{total_restock:,.0f}</div>
                    <div class="kpi-label">unit</div>
                </div>
                """, unsafe_allow_html=True)
            with col4:
                st.markdown(f"""
                <div class="kpi-card" style="background: linear-gradient(135deg, #0d4e8c 0%, #1f77b4 100%);">
                    <div class="kpi-label">Risiko Stockout</div>
                    <div class="kpi-value">{total_stockout:,.0f}</div>
                    <div class="kpi-label">unit berpotensi hilang</div>
                </div>
                """, unsafe_allow_html=True)

            # ===== ALERT =====
            kritis = df_pred[df_pred["Urgensi"] == "🔴 Kritis"]
            if not kritis.empty:
                alert_lines = [
                    f"- **{row['Kategori']}**: prediksi {row['Prediksi Minggu Depan']:,.0f} unit, "
                    f"stok {row['Stok Saat Ini']:,.0f} → **restock {row['Restock Diperlukan']:,.0f} unit**"
                    for _, row in kritis.iterrows()
                ]
                st.error(f"🔴 **{len(kritis)} Kategori Risiko Stockout Tinggi:**\n\n" + "\n\n".join(alert_lines))

            # ===== TABEL =====
            st.divider()
            st.subheader("🎯 Daftar Keputusan Restock")
            st.dataframe(df_pred, use_container_width=True, hide_index=True)

            # ===== GRAFIK =====
            st.divider()
            st.subheader("📊 Visualisasi Stockout Risk")

            fig = go.Figure()
            fig.add_trace(go.Bar(
                name="Penjualan Minggu Lalu",
                x=df_pred["Kategori"], y=df_pred["Penjualan Minggu Lalu"],
                marker_color="#94a3b8",
            ))
            fig.add_trace(go.Bar(
                name="Stok Saat Ini",
                x=df_pred["Kategori"], y=df_pred["Stok Saat Ini"],
                marker_color="#2a9d8f",
            ))
            fig.add_trace(go.Bar(
                name="Prediksi Minggu Depan",
                x=df_pred["Kategori"], y=df_pred["Prediksi Minggu Depan"],
                marker_color="#1f77b4",
            ))
            fig.add_trace(go.Bar(
                name="Restock Diperlukan",
                x=df_pred["Kategori"], y=df_pred["Restock Diperlukan"],
                marker_color="#e63946",
            ))
            fig.update_layout(
                barmode="group", xaxis_title="", yaxis_title="Unit",
                height=480, xaxis_tickangle=-45,
                title="Perbandingan: Penjualan vs Stok vs Prediksi vs Restock",
            )
            st.plotly_chart(fig, use_container_width=True)

            # ===== EXPORT =====
            st.divider()
            csv = df_pred.to_csv(index=False).encode("utf-8")
            st.download_button(
                "📥 Download Keputusan Restock (CSV)",
                data=csv,
                file_name=f"keputusan_restock_{datetime.now().strftime('%Y%m%d')}.csv",
                mime="text/csv",
                use_container_width=True,
            )


# ============================================================
# HALAMAN 6: RIWAYAT & LAPORAN
# ============================================================
elif page == "📜 Riwayat & Laporan":
    st.header("📜 Riwayat & Laporan")
    st.caption("Semua prediksi & rekomendasi restock yang pernah dilakukan")

    col1, col2 = st.columns([3, 1])
    with col1:
        limit = st.slider("Tampilkan riwayat terakhir:", 5, 100, 20, 5)
    with col2:
        if st.button("🔄 Refresh", use_container_width=True):
            st.rerun()

    history = get_history(limit)

    if "error" in history:
        st.error(f"⚠️ {history['error']}")
    elif not history:
        st.info("Belum ada riwayat. Coba lakukan prediksi di halaman 🔮 atau 🏠.")
    else:
        df_hist = pd.DataFrame(history)
        df_hist["created_at"] = pd.to_datetime(df_hist["created_at"]).dt.strftime("%d %b %Y, %H:%M")
        df_hist = df_hist.rename(columns={
            "id": "ID",
            "kategori": "Kategori Obat",
            "predicted_qty": "Prediksi (unit)",
            "recommendation_restock": "Rekomendasi Restock (unit)",
            "buffer_pct": "Buffer (%)",
            "created_at": "Waktu Prediksi",
        })

        st.subheader("📊 Ringkasan")
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Total Prediksi", f"{len(df_hist)}")
        with col2:
            st.metric("Total Unit Diprediksi", f"{df_hist['Prediksi (unit)'].sum():,.0f}")
        with col3:
            st.metric("Total Restock Direkomendasikan", f"{df_hist['Rekomendasi Restock (unit)'].sum():,.0f}")

        st.divider()
        st.subheader("📋 Detail Riwayat")
        st.dataframe(df_hist, use_container_width=True, hide_index=True)

        csv = df_hist.to_csv(index=False).encode("utf-8")
        st.download_button(
            "📥 Download Riwayat (CSV)", data=csv,
            file_name=f"riwayat_prediksi_{datetime.now().strftime('%Y%m%d')}.csv",
            mime="text/csv",
        )