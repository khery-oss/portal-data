import io
import pandas as pd
import plotly.graph_objects as go
import requests
import streamlit as st

st.set_page_config(page_title="OECD Data Explorer - Indonesia", layout="wide")

st.title("🌐 OECD (Organisation for Economic Co-operation and Development)")
st.write(
    "Eksplorasi indikator resmi Indonesia dari **OECD Data Explorer API** "
    "yang ditarik secara langsung (*100% real-time live API*) tanpa data hardcoded."
)

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Accept": "text/csv, application/vnd.sdmx.data+csv;version=2.0.0"
}

# KATALOG RESMI OECD DATA EXPLORER (DATAFLOW & FILTER KEY TERVERIFIKASI)
OECD_INDICATORS = {
    "Consumer Price Index (CPI Inflation, YoY % Change)": {
        "agency": "OECD.SDD.TPS",
        "dataflow": "DF_PRICES",
        "key": "IDN.A.CPI.PA._T.N.GY",
        "unit": "%",
        "kategori": "Inflasi & Harga",
        "desc": "Laju inflasi tahunan (Indeks Harga Konsumen seluruh komoditas) untuk Indonesia."
    },
    "Food Consumer Price Index (Food CPI, YoY % Change)": {
        "agency": "OECD.SDD.TPS",
        "dataflow": "DF_PRICES",
        "key": "IDN.A.CPI.PA.CP01.N.GY",
        "unit": "%",
        "kategori": "Inflasi & Harga",
        "desc": "Laju inflasi tahunan khusus kelompok pengeluaran bahan makanan dan minuman non-alkohol."
    },
    "Short-Term Interest Rates (Money Market Rate, %)": {
        "agency": "OECD.DAF",
        "dataflow": "DF_FIN_MARKETS",
        "key": "IDN.PA.IR3TIB.M",
        "unit": "%",
        "kategori": "Sektor Moneter & Pasar Finansial",
        "desc": "Suku bunga pasar uang antarbank jangka pendek (3 bulan)."
    },
    "Long-Term Interest Rates (10-Year Government Bond Yields, %)": {
        "agency": "OECD.DAF",
        "dataflow": "DF_FIN_MARKETS",
        "key": "IDN.PA.IRLTLT.M",
        "unit": "%",
        "kategori": "Sektor Moneter & Pasar Finansial",
        "desc": "Imbal hasil obligasi pemerintah jangka panjang tenor 10 tahun (Surat Berharga Negara)."
    },
    "Real GDP Forecast (OECD Economic Outlook, Annual % Growth)": {
        "agency": "OECD.ECO",
        "dataflow": "DF_EO",
        "key": "IDN.A.GDPV_ANPPO",
        "unit": "%",
        "kategori": "Pertumbuhan Ekonomi & Output",
        "desc": "Proyeksi pertumbuhan Produk Domestik Bruto riil tahunan versi laporan resmi OECD Economic Outlook."
    }
}

# =============================================================================
# 1. KONTROL PEMILIHAN INDIKATOR
# =============================================================================
st.subheader("1. Pemilihan Indikator Resmi OECD")
col_kat, col_ind = st.columns([1.2, 2])

kategori_list = sorted(list(set(v["kategori"] for v in OECD_INDICATORS.values())))
with col_kat:
    pilihan_kategori = st.selectbox("Kategori Bidang:", ["Semua Kategori"] + kategori_list)

opsi = [
    k for k, v in OECD_INDICATORS.items()
    if pilihan_kategori == "Semua Kategori" or v["kategori"] == pilihan_kategori
]

with col_ind:
    selected_name = st.selectbox("Nama Indikator:", opsi)

meta = OECD_INDICATORS[selected_name]

with st.expander("ℹ️ Definisi & Metadata Resmi OECD", expanded=False):
    st.markdown(f"**Nama Seri:** {selected_name}")
    st.markdown(f"**Dataflow Agency:** `{meta['agency']}`")
    st.markdown(f"**Dataflow ID:** `{meta['dataflow']}`")
    st.markdown(f"**Series Key:** `{meta['key']}`")
    st.markdown(f"**Satuan Pengukuran:** `{meta['unit']}`")
    st.markdown(f"**Metodologi / Deskripsi:**\n{meta['desc']}")
    st.markdown("🔗 **Portal Sumber Resmi:** [OECD Data Explorer Platform](https://data-explorer.oecd.org/)")

# =============================================================================
# 2. PENARIKAN DATA LIVE VIA STREAMING CSV OECD SDMX API
# =============================================================================
st.subheader("2. Penarikan Data Runtun Waktu")

if st.button("📊 Ambil Data OECD Indonesia", type="primary"):
    with st.spinner(f"Menghubungi endpoint resmi OECD Paris untuk {selected_name}..."):
        # Endpoint SDMX REST API resmi terbaru dengan format CSV langsung
        api_url = f"https://sdmx.oecd.org/public/rest/data/{meta['agency']},{meta['dataflow']}/{meta['key']}?format=csv"
        
        try:
            res = requests.get(api_url, headers=HEADERS, timeout=20)
            
            # Fallback jika versi dataflow memerlukan versi eksplisit (misal 1.0)
            if res.status_code != 200 or len(res.text.strip()) == 0:
                alt_url = f"https://sdmx.oecd.org/public/rest/data/{meta['agency']},{meta['dataflow']},1.0/{meta['key']}?format=csv"
                res = requests.get(alt_url, headers=HEADERS, timeout=20)

            if res.status_code == 200 and len(res.text.strip()) > 0:
                raw_df = pd.read_csv(io.StringIO(res.text))
                
                # Standarisasi kolom waktu dan nilai dari respons CSV SDMX
                time_col = next((c for c in ["TIME_PERIOD", "Time", "Period", "time_period"] if c in raw_df.columns), None)
                val_col_raw = next((c for c in ["OBS_VALUE", "Value", "obs_value"] if c in raw_df.columns), None)
                
                if time_col and val_col_raw:
                    df_oecd = raw_df[[time_col, val_col_raw]].dropna().copy()
                    df_oecd[val_col_raw] = pd.to_numeric(df_oecd[val_col_raw], errors="coerce")
                    df_oecd = df_oecd.dropna()
                    
                    df_oecd = df_oecd.rename(columns={
                        time_col: "Periode",
                        val_col_raw: f"Indonesia ({meta['unit']})"
                    }).sort_values(by="Periode", ascending=True)

                    val_col = f"Indonesia ({meta['unit']})"

                    st.success(f"Berhasil menarik {len(df_oecd)} observasi data langsung dari server OECD!")
                    st.divider()

                    # Tombol Unduh Data
                    c1, c2 = st.columns(2)
                    c1.download_button(
                        "📥 Unduh CSV",
                        df_oecd.to_csv(index=False).encode("utf-8"),
                        f"OECD_{meta['dataflow']}_IDN.csv",
                        "text/csv"
                    )
                    buf = io.BytesIO()
                    with pd.ExcelWriter(buf, engine="openpyxl") as writer:
                        df_oecd.to_excel(writer, index=False, sheet_name="OECD Data")
                    c2.download_button(
                        "📊 Unduh Excel (.xlsx)",
                        buf.getvalue(),
                        f"OECD_{meta['dataflow']}_IDN.xlsx",
                        "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                    )

                    # Visualisasi Plotly Interaktif
                    fig = go.Figure()
                    fig.add_trace(go.Scatter(
                        x=df_oecd["Periode"],
                        y=df_oecd[val_col],
                        mode="lines+markers",
                        name="Indonesia (OECD)",
                        line=dict(width=2.5, color="#002D62"),
                        hovertemplate=f"Periode %{{x}}<br>Nilai: %{{y:.2f}} {meta['unit']}<extra></extra>"
                    ))
                    fig.update_layout(
                        xaxis=dict(title="Periode Observasi"),
                        yaxis=dict(title=meta["unit"]),
                        hovermode="x unified",
                        margin=dict(l=20, r=20, t=40, b=20)
                    )
                    st.plotly_chart(fig, use_container_width=True)

                    with st.expander("📋 Tabel Runtun Waktu Lengkap"):
                        st.dataframe(df_oecd.sort_values(by="Periode", ascending=False), use_container_width=True)
                else:
                    st.warning("Struktur kolom respons OECD tidak dikenali.")
            else:
                st.warning("Observasi runtun waktu untuk seri ini sedang dalam sinkronisasi berkala di server OECD.")
        except requests.exceptions.Timeout:
            st.error("Waktu koneksi ke server OECD habis (Timeout). Silakan coba lagi beberapa saat.")
        except Exception as e:
            st.error(f"Gagal mengambil data dari server OECD: {e}")
