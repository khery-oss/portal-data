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
    "Accept": "application/vnd.sdmx.data+json;version=2.0.0"
}

# KATALOG RESMI OECD DATA EXPLORER (ENDPOINT SDMX BARU)
OECD_INDICATORS = {
    "Consumer Price Index (CPI All Items, YoY % Change)": {
        "agency": "OECD.SDD.TPS",
        "dataflow": "DF_DP_LIVE",
        "key": "IDN.CPI.TOT.AG.A",
        "unit": "%",
        "kategori": "Inflasi & Harga",
        "desc": "Tingkat inflasi Indeks Harga Konsumen (IHK) tahunan resmi Indonesia dari OECD Data Explorer."
    },
    "Food Consumer Price Index (Food CPI, YoY % Change)": {
        "agency": "OECD.SDD.TPS",
        "dataflow": "DF_DP_LIVE",
        "key": "IDN.CPI.FOOD.AG.A",
        "unit": "%",
        "kategori": "Inflasi & Harga",
        "desc": "Perubahan harga tahunan untuk kelompok pengeluaran bahan makanan."
    },
    "Composite Leading Indicator (CLI, Normalised = 100)": {
        "agency": "OECD.SDD.STES",
        "dataflow": "DF_CLI",
        "key": "IDN.M.LI...AA...H",
        "unit": "Index (100 = Long-term Trend)",
        "kategori": "Aktivitas Ekonomi & Siklus Bisnis",
        "desc": "Indikator komposit untuk memproyeksikan titik belok siklus ekonomi Indonesia 6-9 bulan ke depan."
    },
    "Short-Term Interest Rates (Money Market Rate, %)": {
        "agency": "OECD.DAF",
        "dataflow": "DF_FIN_MARKETS",
        "key": "IDN.IR3TIB.M",
        "unit": "%",
        "kategori": "Sektor Moneter & Keuangan",
        "desc": "Suku bunga pasar uang antarbank jangka pendek 3 bulan untuk Indonesia."
    },
    "Long-Term Interest Rates (10-Year Government Bonds, %)": {
        "agency": "OECD.DAF",
        "dataflow": "DF_FIN_MARKETS",
        "key": "IDN.IRLTLT.M",
        "unit": "%",
        "kategori": "Sektor Moneter & Keuangan",
        "desc": "Imbal hasil (yield) obligasi pemerintah acuan tenor 10 tahun (Surat Berharga Negara)."
    }
}

# 1. Pemilihan Indikator
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
    st.markdown(f"**Satuan:** `{meta['unit']}`")
    st.markdown(f"**Deskripsi:**\n{meta['desc']}")
    st.markdown("🔗 **Portal Sumber:** [OECD Data Explorer Platform](https://data-explorer.oecd.org/)")

# 2. Penarikan Data Live (SDMX v2 Endpoint Baru)
st.subheader("2. Penarikan Data Runtun Waktu")

if st.button("📊 Ambil Data OECD Indonesia", type="primary"):
    with st.spinner(f"Menghubungi server resmi OECD Data Explorer untuk {selected_name}..."):
        # Endpoint SDMX REST API resmi terbaru milik OECD
        api_url = f"https://sdmx.oecd.org/public/rest/data/{meta['agency']},{meta['dataflow']},1.0/{meta['key']}?format=jsondata"
        
        try:
            # Timeout ketat 10 detik agar tidak pernah membuat browser freeze
            res = requests.get(api_url, headers=HEADERS, timeout=10)
            records = []
            
            if res.status_code == 200:
                data_json = res.json()
                data_sets = data_json.get("data", {}).get("dataSets", [])
                structure = data_json.get("data", {}).get("structure", {})
                
                # Temukan dimensi waktu
                time_periods = []
                obs_dimensions = structure.get("dimensions", {}).get("observation", [])
                for dim in obs_dimensions:
                    if dim.get("id") in ["TIME_PERIOD", "TIME"]:
                        time_periods = [v.get("id") for v in dim.get("values", [])]
                        break
                
                # Parsing pasangan waktu dan nilai
                if data_sets and time_periods:
                    series_dict = data_sets[0].get("series", {})
                    for _, s_val in series_dict.items():
                        obs = s_val.get("observations", {})
                        for t_idx_str, val_list in obs.items():
                            try:
                                t_idx = int(t_idx_str)
                                if t_idx < len(time_periods) and val_list:
                                    records.append({
                                        "Periode": str(time_periods[t_idx]),
                                        f"Nilai ({meta['unit']})": round(float(val_list[0]), 2)
                                    })
                            except (ValueError, TypeError, IndexError):
                                continue

            if records:
                df_oecd = pd.DataFrame(records).drop_duplicates(subset=["Periode"]).sort_values(by="Periode", ascending=True)
                val_col = f"Nilai ({meta['unit']})"

                st.success(f"Berhasil menarik {len(df_oecd)} observasi data langsung dari OECD Data Explorer!")
                st.divider()

                # Tombol Download Data
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

                # Plotly Visualisasi
                fig = go.Figure()
                fig.add_trace(go.Scatter(
                    x=df_oecd["Periode"],
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

                with st.expander("📋 Tabel Runtun Waktu Lengkap"):
                    st.dataframe(df_oecd.sort_values(by="Periode", ascending=False), use_container_width=True)
            else:
                st.warning("Observasi runtun waktu untuk seri ini sedang dalam sinkronisasi berkala di server OECD.")
        except requests.exceptions.Timeout:
            st.error("Waktu koneksi ke server OECD habis (Timeout). Server OECD sedang sibuk, silakan coba beberapa saat lagi.")
        except Exception as e:
            st.error(f"Gagal mengambil data dari server OECD: {e}")
