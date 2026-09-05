import io
import pandas as pd
import plotly.graph_objects as go
import requests
import streamlit as st

st.set_page_config(page_title="OECD CLI Explorer - Indonesia", layout="wide")

st.title("🌐 OECD - Composite Leading Indicators (CLI)")
st.write(
    "Eksplorasi indikator resmi **Composite Leading Indicators (CLI)** dari **OECD Data Explorer API** "
    "khusus untuk **Indonesia (Key Partner OECD: IDN)** secara langsung (*100% real-time live API*)."
)

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
}

# KATALOG RESMI OECD DATAFLOW CLI YANG AKTIF MENGEMBALIKAN DATA INDONESIA
OECD_CLI_CATALOG = {
    "CLI Amplitude Adjusted (Long-term Trend = 100)": {
        "url": "https://sdmx.oecd.org/public/rest/data/OECD.SDD.STES,DSD_STES@DF_CLI/IDN.M.LI...AA...H?dimensionAtObservation=AllDimensions&format=csvfilewithlabels",
        "unit": "Indeks (100 = Tren)",
        "desc": "Indikator komposit resmi OECD yang dirancang untuk mendeteksi titik belok (turning points) siklus ekonomi Indonesia 6–9 bulan ke depan."
    },
    "CLI Normalized (Economic Cycle Turning Points)": {
        "url": "https://sdmx.oecd.org/public/rest/data/OECD.SDD.STES,DSD_STES@DF_CLI/IDN.M.LI...NORM...H?dimensionAtObservation=AllDimensions&format=csvfilewithlabels",
        "unit": "Indeks Ternormalisasi",
        "desc": "Indikator siklus ekonomi murni tanpa komponen tren; nilai di atas 100 mengindikasikan fase ekspansi, di bawah 100 menunjukkan perlambatan."
    },
    "CLI 12-Month Rate of Change (% YoY Growth)": {
        "url": "https://sdmx.oecd.org/public/rest/data/OECD.SDD.STES,DSD_STES@DF_CLI/IDN.M.LI...GY...H?dimensionAtObservation=AllDimensions&format=csvfilewithlabels",
        "unit": "% YoY",
        "desc": "Laju perubahan tahunan indikator komposit untuk mengukur akselerasi atau deselerasi momentum perekonomian."
    },
    "CLI Trend Restored (Short-term Economic Activity Level)": {
        "url": "https://sdmx.oecd.org/public/rest/data/OECD.SDD.STES,DSD_STES@DF_CLI/IDN.M.LI...TR...H?dimensionAtObservation=AllDimensions&format=csvfilewithlabels",
        "unit": "Tingkat Aktivitas",
        "desc": "Tingkat aktivitas ekonomi riil jangka pendek yang dikombinasikan kembali dengan garis tren jangka panjang."
    }
}

# =============================================================================
# 1. PEMILIHAN INDIKATOR
# =============================================================================
st.subheader("1. Pemilihan Seri OECD Composite Leading Indicators")

selected_name = st.selectbox("Pilih Varian Indikator CLI Indonesia:", list(OECD_CLI_CATALOG.keys()))
meta = OECD_CLI_CATALOG[selected_name]

with st.expander("ℹ️ Definisi & Metodologi Resmi OECD CLI", expanded=False):
    st.markdown(f"**Nama Seri:** {selected_name}")
    st.markdown(f"**Dataflow OECD:** `OECD.SDD.STES,DSD_STES@DF_CLI`")
    st.markdown(f"**Satuan Pengukuran:** `{meta['unit']}`")
    st.markdown(f"**Deskripsi Metodologi:**\n{meta['desc']}")
    st.markdown("🔗 **Portal Sumber:** [OECD Data Explorer](https://data-explorer.oecd.org/)")

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
                        st.success(f"Berhasil menarik {len(df_oecd)} observasi bulanan langsung dari server resmi OECD!")
                        st.divider()

                        # Unduh Data
                        c1, c2 = st.columns(2)
                        c1.download_button(
                            "📥 Unduh CSV",
                            df_oecd.to_csv(index=False).encode("utf-8"),
                            f"OECD_IDN_CLI.csv",
                            "text/csv"
                        )
                        buf = io.BytesIO()
                        with pd.ExcelWriter(buf, engine="openpyxl") as writer:
                            df_oecd.to_excel(writer, index=False, sheet_name="OECD CLI Data")
                        c2.download_button(
                            "📊 Unduh Excel (.xlsx)",
                            buf.getvalue(),
                            f"OECD_IDN_CLI.xlsx",
                            "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                        )

                        # Visualisasi Plotly
                        fig = go.Figure()
                        fig.add_trace(go.Scatter(
                            x=df_oecd["Periode"],
                            y=df_oecd[val_col],
                            mode="lines",
                            name="Indonesia (OECD CLI)",
                            line=dict(width=2.5, color="#002D62"),
                            hovertemplate="Periode: %{x}<br>Nilai: %{y:.2f}<extra></extra>"
                        ))
                        
                        # Garis batas acuan 100 untuk CLI
                        if "100" in meta["unit"] or "Ternormalisasi" in meta["unit"]:
                            fig.add_hline(y=100, line_dash="dash", line_color="red", annotation_text="Ambang Batas Tren (100)")

                        fig.update_layout(
                            xaxis=dict(title="Periode Observasi (Bulanan)"),
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
                    st.warning("Struktur data yang dikembalikan tidak sesuai format standar OECD.")
            else:
                st.warning("Koneksi ke endpoint OECD tidak mengembalikan data. Silakan coba beberapa saat lagi.")
        except requests.exceptions.Timeout:
            st.error("Waktu koneksi ke server OECD habis (Timeout).")
        except Exception as e:
            st.error(f"Gagal mengambil data dari server OECD: {e}")
