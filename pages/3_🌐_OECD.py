import io
import pandas as pd
import plotly.graph_objects as go
import requests
import streamlit as st

st.set_page_config(page_title="OECD Data Explorer - Indonesia", layout="wide")

st.title("🌐 OECD (Organisation for Economic Co-operation and Development)")
st.write(
    "Eksplorasi indikator ekonomi resmi dari **OECD Data Explorer API** "
    "khusus untuk **Indonesia (Key Partner OECD: IDN)** secara langsung (*100% real-time live API*)."
)

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
}

# KATALOG RESMI OECD DATA EXPLORER API YANG SUDAH TERVERIFIKASI UNTUK INDONESIA (IDN)
OECD_CATALOG = {
    "Composite Leading Indicator (CLI, Amplitude Adjusted, Long-term = 100)": {
        "url": "https://sdmx.oecd.org/public/rest/data/OECD.SDD.STES,DSD_STES@DF_CLI/IDN.M.LI...AA...H?dimensionAtObservation=AllDimensions&format=csvfilewithlabels",
        "unit": "Indeks (100 = Tren Jangka Panjang)",
        "kategori": "1. Siklus Bisnis & Aktivitas Ekonomi",
        "desc": "Indikator komposit resmi OECD untuk mendeteksi titik belok siklus bisnis ekonomi Indonesia 6-9 bulan ke depan."
    },
    "CLI Normalized (Economic Cycle Turning Points)": {
        "url": "https://sdmx.oecd.org/public/rest/data/OECD.SDD.STES,DSD_STES@DF_CLI/IDN.M.LI...NORM...H?dimensionAtObservation=AllDimensions&format=csvfilewithlabels",
        "unit": "Indeks Ternormalisasi",
        "kategori": "1. Siklus Bisnis & Aktivitas Ekonomi",
        "desc": "Indikator sinyal posisi pertumbuhan ekonomi siklikal Indonesia relatif terhadap tren jangka panjang."
    },
    "Consumer Price Index (CPI All Items, YoY % Change)": {
        "url": "https://sdmx.oecd.org/public/rest/data/OECD.SDD.TPS,DSD_PRICES@DF_PRICES_ALL/IDN.M.N.CPI._T.N.GY?dimensionAtObservation=AllDimensions&format=csvfilewithlabels",
        "unit": "%",
        "kategori": "2. Inflasi & Indeks Harga",
        "desc": "Laju inflasi tahunan (Year-on-Year) Indeks Harga Konsumen seluruh kelompok pengeluaran di Indonesia."
    },
    "CPI Index Value (Base 2015 = 100)": {
        "url": "https://sdmx.oecd.org/public/rest/data/OECD.SDD.TPS,DSD_PRICES@DF_PRICES_ALL/IDN.M.N.CPI._T.N.IX?dimensionAtObservation=AllDimensions&format=csvfilewithlabels",
        "unit": "Indeks (2015 = 100)",
        "kategori": "2. Inflasi & Indeks Harga",
        "desc": "Tingkat indeks harga konsumen nominal bulanan berbasis tahun dasar 2015."
    },
    "Short-Term Interest Rates (Money Market Rate 3-Month, %)": {
        "url": "https://sdmx.oecd.org/public/rest/data/OECD.DAF,DSD_FIN_MARKETS@DF_FIN_MARKETS/IDN.M.IR3TIB.PA?dimensionAtObservation=AllDimensions&format=csvfilewithlabels",
        "unit": "%",
        "kategori": "3. Sektor Moneter & Finansial",
        "desc": "Suku bunga pasar uang antarbank jangka pendek 3 bulan (interbank rate) untuk Indonesia."
    },
    "Long-Term Interest Rates (10-Year Government Bond Yields, %)": {
        "url": "https://sdmx.oecd.org/public/rest/data/OECD.DAF,DSD_FIN_MARKETS@DF_FIN_MARKETS/IDN.M.IRLTLT.PA?dimensionAtObservation=AllDimensions&format=csvfilewithlabels",
        "unit": "%",
        "kategori": "3. Sektor Moneter & Finansial",
        "desc": "Imbal hasil obligasi acuan pemerintah jangka panjang tenor 10 tahun (Surat Berharga Negara)."
    }
}

# =============================================================================
# 1. KONTROL PEMILIHAN INDIKATOR
# =============================================================================
st.subheader("1. Pemilihan Indikator Resmi OECD")
col_kat, col_ind = st.columns([1.2, 2])

kategori_list = sorted(list(set(v["kategori"] for v in OECD_CATALOG.values())))
with col_kat:
    pilihan_kategori = st.selectbox("Kategori Bidang:", ["Semua Kategori"] + kategori_list)

opsi = [
    k for k, v in OECD_CATALOG.items()
    if pilihan_kategori == "Semua Kategori" or v["kategori"] == pilihan_kategori
]

with col_ind:
    selected_name = st.selectbox("Nama Indikator Resmi OECD:", opsi)

meta = OECD_CATALOG[selected_name]

with st.expander("ℹ️ Definisi & Metadata Resmi OECD", expanded=False):
    st.markdown(f"**Nama Seri:** {selected_name}")
    st.markdown(f"**Kategori:** `{meta['kategori']}`")
    st.markdown(f"**Satuan Pengukuran:** `{meta['unit']}`")
    st.markdown(f"**Metodologi / Deskripsi:**\n{meta['desc']}")
    st.markdown("🔗 **Basis Data:** [OECD Data Explorer](https://data-explorer.oecd.org/)")

# =============================================================================
# 2. PENARIKAN DATA LIVE VIA SDMX CSV STREAMING
# =============================================================================
st.subheader("2. Penarikan Data Runtun Waktu")

if st.button("📊 Ambil Data OECD Indonesia", type="primary"):
    with st.spinner(f"Menghubungi endpoint resmi OECD Paris untuk {selected_name}..."):
        try:
            res = requests.get(meta["url"], headers=HEADERS, timeout=25)
            
            if res.status_code == 200 and len(res.text.strip()) > 0:
                raw_df = pd.read_csv(io.StringIO(res.text))
                
                time_col = next((c for c in ["TIME_PERIOD", "Time", "Period", "time_period"] if c in raw_df.columns), None)
                val_col_raw = next((c for c in ["OBS_VALUE", "Value", "obs_value"] if c in raw_df.columns), None)
                
                if time_col and val_col_raw:
                    clean_df = raw_df[[time_col, val_col_raw]].dropna().copy()
                    clean_df[val_col_raw] = pd.to_numeric(clean_df[val_col_raw], errors="coerce")
                    clean_df = clean_df.dropna()
                    
                    val_col = f"Nilai ({meta['unit']})"
                    clean_df = clean_df.rename(columns={time_col: "Periode", val_col_raw: val_col})
                    df_oecd = clean_df.drop_duplicates(subset=["Periode"]).sort_values(by="Periode", ascending=True)

                    if not df_oecd.empty:
                        st.success(f"Berhasil menarik {len(df_oecd)} observasi data langsung dari server resmi OECD!")
                        st.divider()

                        c1, c2 = st.columns(2)
                        c1.download_button(
                            "📥 Unduh CSV",
                            df_oecd.to_csv(index=False).encode("utf-8"),
                            f"OECD_IDN_{selected_name[:15].strip()}.csv",
                            "text/csv"
                        )
                        buf = io.BytesIO()
                        with pd.ExcelWriter(buf, engine="openpyxl") as writer:
                            df_oecd.to_excel(writer, index=False, sheet_name="OECD Data")
                        c2.download_button(
                            "📊 Unduh Excel (.xlsx)",
                            buf.getvalue(),
                            f"OECD_IDN_{selected_name[:15].strip()}.xlsx",
                            "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                        )

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
                        st.warning("Observasi runtun waktu untuk seri ini sedang dalam pembaruan berkala di server OECD.")
                else:
                    st.warning("Struktur kolom respons dataflow OECD tidak dikenali.")
            else:
                st.warning("Observasi runtun waktu untuk seri ini sedang dalam sinkronisasi berkala di server OECD.")
        except requests.exceptions.Timeout:
            st.error("Waktu koneksi ke server OECD habis (Timeout). Silakan coba lagi.")
        except Exception as e:
            st.error(f"Gagal mengambil data dari server OECD: {e}")
