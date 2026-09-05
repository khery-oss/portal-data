import io
import pandas as pd
import plotly.graph_objects as go
import requests
import streamlit as st

st.set_page_config(page_title="OECD Data Explorer - Indonesia", layout="wide")

st.title("🌐 OECD (Organisation for Economic Co-operation and Development)")
st.write(
    "Eksplorasi indikator ekonomi utama Indonesia dari **OECD Data API** "
    "yang ditarik secara **100% langsung (*real-time live API*)** dari server resmi OECD."
)

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Accept": "application/vnd.sdmx.data+json;version=1.0.0-wd"
}

# KATALOG DATAFLOW RESMI OECD UNTUK INDONESIA (KEY PARTNER: IDN)
OECD_INDICATORS = {
    "Consumer Price Index (CPI Inflation, % Change YoY)": {
        "dataset": "PRICES_CPI",
        "query": "IDN.CPALTT01.GY.A",
        "unit": "%",
        "kategori": "Inflasi & Harga",
        "desc": "Tingkat inflasi tahunan (Indeks Harga Konsumen seluruh item) untuk Indonesia."
    },
    "Core Inflation (CPI excluding Food and Energy, % YoY)": {
        "dataset": "PRICES_CPI",
        "query": "IDN.CPGRLE01.GY.A",
        "unit": "%",
        "kategori": "Inflasi & Harga",
        "desc": "Inflasi inti yang mengecualikan komponen bergejolak seperti makanan dan energi."
    },
    "Composite Leading Indicator (CLI, Normalised = 100)": {
        "dataset": "MEI_CLI",
        "query": "LOLITOAA.IDN.M",
        "unit": "Indeks (100 = Tren Jangka Panjang)",
        "kategori": "Siklus Bisnis & Aktivitas Ekonomi",
        "desc": "Indikator komposit untuk mendeteksi titik balik siklus bisnis ekonomi Indonesia 6-9 bulan ke depan."
    },
    "Long-Term Government Bond Yields (10-Year, %)": {
        "dataset": "MEI_FIN",
        "query": "IRLTLT01.IDN.M",
        "unit": "%",
        "kategori": "Sektor Keuangan & Moneter",
        "desc": "Imbal hasil (yield) obligasi pemerintah Indonesia tenor 10 tahun (Surat Berharga Negara)."
    },
    "Short-Term Interest Rates (Money Market Rate, %)": {
        "dataset": "MEI_FIN",
        "query": "IR3TIB01.IDN.M",
        "unit": "%",
        "kategori": "Sektor Keuangan & Moneter",
        "desc": "Suku bunga pasar uang antar bank jangka pendek 3 bulan."
    },
    "Real GDP Growth (Quarterly / Annual Forecast, %)": {
        "dataset": "EO",
        "query": "IDN.GDPV_ANPPO.A",
        "unit": "%",
        "kategori": "Pertumbuhan Ekonomi & Output",
        "desc": "Pertumbuhan tahunan Produk Domestik Bruto riil Indonesia versi proyeksi resmi OECD Economic Outlook."
    }
}

# 1. Kontrol Pemilihan Indikator
st.subheader("1. Pemilihan Indikator Resmi OECD")
col_kat, col_ind = st.columns([1.2, 2])

kategori_list = sorted(list(set(v["kategori"] for v in OECD_INDICATORS.values())))
with col_kat:
    pilihan_kategori = st.selectbox("Kategori Bidang:", ["Semua Kategori"] + kategori_list)

opsi_indikator = [
    k for k, v in OECD_INDICATORS.items()
    if pilihan_kategori == "Semua Kategori" or v["kategori"] == pilihan_kategori
]

with col_ind:
    selected_name = st.selectbox("Nama Indikator:", opsi_indikator)

meta = OECD_INDICATORS[selected_name]

with st.expander("ℹ️ Definisi & Metadata Resmi OECD", expanded=False):
    st.markdown(f"**Nama Seri:** {selected_name}")
    st.markdown(f"**OECD Dataflow:** `{meta['dataset']}`")
    st.markdown(f"**Query Parameter:** `{meta['query']}`")
    st.markdown(f"**Satuan Pengukuran:** `{meta['unit']}`")
    st.markdown(f"**Metodologi / Deskripsi:**\n{meta['desc']}")
    st.markdown("🔗 **Basis Data:** [OECD Data Explorer Portal](https://data-explorer.oecd.org/)")

# 2. Penarikan Data Live via SDMX-JSON API Resmi OECD
st.subheader("2. Penarikan Data Runtun Waktu")

if st.button("📊 Ambil Data OECD Indonesia", type="primary"):
    with st.spinner(f"Menghubungi endpoint resmi OECD Paris untuk {selected_name}..."):
        api_url = f"https://stats.oecd.org/SDMX-JSON/data/{meta['dataset']}/{meta['query']}/all?contentType=csv"
        
        try:
            # Mengambil data langsung dari endpoint CSV streaming OECD
            r = requests.get(api_url, headers=HEADERS, timeout=25)
            
            if r.status_code == 200 and len(r.text.strip()) > 0:
                raw_df = pd.read_csv(io.StringIO(r.text))
                
                # Standarisasi nama kolom dari respons resmi OECD
                time_col = next((col for col in ["TIME_PERIOD", "Time", "Period"] if col in raw_df.columns), None)
                val_col_raw = next((col for col in ["OBS_VALUE", "Value"] if col in raw_df.columns), None)
                
                if time_col and val_col_raw:
                    df_oecd = raw_df[[time_col, val_col_raw]].dropna().rename(
                        columns={time_col: "Waktu", val_col_raw: f"Indonesia ({meta['unit']})"}
                    )
                    df_oecd = df_oecd.sort_values(by="Waktu", ascending=True)
                    val_col = f"Indonesia ({meta['unit']})"

                    st.success(f"Berhasil menarik {len(df_oecd)} data observasi langsung dari server OECD!")
                    
                    st.divider()
                    st.markdown("🔗 **Tautan Resmi:** [OECD Data Explorer](https://data-explorer.oecd.org/)")

                    # Tombol Unduh
                    c1, c2 = st.columns(2)
                    c1.download_button(
                        "📥 Unduh CSV",
                        df_oecd.to_csv(index=False).encode("utf-8"),
                        f"OECD_{meta['dataset']}_IDN.csv",
                        "text/csv"
                    )
                    buf = io.BytesIO()
                    with pd.ExcelWriter(buf, engine="openpyxl") as writer:
                        df_oecd.to_excel(writer, index=False, sheet_name="OECD Data")
                    c2.download_button(
                        "📊 Unduh Excel (.xlsx)",
                        buf.getvalue(),
                        f"OECD_{meta['dataset']}_IDN.xlsx",
                        "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                    )

                    # Visualisasi Plotly
                    fig = go.Figure()
                    fig.add_trace(go.Scatter(
                        x=df_oecd["Waktu"],
                        y=df_oecd[val_col],
                        mode="lines+markers",
                        name="Indonesia (OECD)",
                        line=dict(width=2.5, color="#002D62"),
                        hovertemplate=f"Periode %{{x}}<br>Nilai: %{{y}} {meta['unit']}<extra></extra>"
                    ))
                    fig.update_layout(
                        xaxis=dict(title="Periode Observasi"),
                        yaxis=dict(title=meta["unit"]),
                        hovermode="x unified",
                        margin=dict(l=20, r=20, t=40, b=20)
                    )
                    st.plotly_chart(fig, use_container_width=True)

                    with st.expander("📋 Tabel Data Runtun Waktu Lengkap"):
                        st.dataframe(df_oecd.sort_values(by="Waktu", ascending=False), use_container_width=True)
                else:
                    st.warning("Struktur data dari OECD tidak memiliki kolom waktu/nilai yang valid.")
            else:
                st.warning("Data untuk seri ini sedang dalam pembaruan berkala di server OECD.")
        except Exception as e:
            st.error(f"Gagal terhubung ke endpoint resmi OECD: {e}")
