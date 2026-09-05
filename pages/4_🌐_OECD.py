import io
import pandas as pd
import plotly.graph_objects as go
import requests
import streamlit as st

st.set_page_config(page_title="OECD Data Explorer - Live API", layout="wide")

st.title("🌐 Portal Data OECD (Live SDMX API)")
st.write(
    "Eksplorasi data makroekonomi dan indikator pembangunan internasional "
    "langsung dari server resmi **OECD**."
)

# Pilihan Indikator yang Diperluas (Menggunakan endpoint statistik umum OECD)
OECD_INDICATORS = {
    "Consumer Price Index (Inflation YoY)": {"code": "PRC_CD", "unit": "Persen (%)"},
    "Gross Domestic Product (GDP Growth Rate)": {"code": "NAAG", "unit": "Persen (%)"},
    "Unemployment Rate": {"code": "MUR", "unit": "Persen (%)"},
    "Total Population": {"code": "POP", "unit": "Jiwa"},
    "General Government Debt (% of GDP)": {"code": "GGDEBT", "unit": "% dari PDB"},
    "Current Account Balance (% of GDP)": {"code": "CAB", "unit": "% dari PDB"}
}

st.subheader("1. Pilih Indikator & Wilayah OECD")
col_1, col_2 = st.columns(2)

with col_1:
    selected_ind_name = st.selectbox("Pilih Seri Indikator:", list(OECD_INDICATORS.keys()))
    ind_meta = OECD_INDICATORS[selected_ind_name]

with col_2:
    country_options = {
        "Indonesia": "IDN",
        "Amerika Serikat": "USA",
        "Jepang": "JPN",
        "Jerman": "DEU",
        "Inggris": "GBR",
        "Korea Selatan": "KOR",
        "Australia": "AUS"
    }
    selected_country_name = st.selectbox("Pilih Negara / Ekonomi:", list(country_options.keys()))
    country_code = country_options[selected_country_name]

if st.button("🌐 Tarik Data OECD Live", type="primary"):
    with st.spinner(f"Menarik data {selected_ind_name} untuk {selected_country_name}..."):
        # Endpoint alternatif OECD SDMX yang lebih stabil untuk berbagai negara
        url = f"https://sdmx.oecd.org/public/rest/data/OECD.SDD.NAD,DSD_NAMAIN1@DF_TABLE1/{country_code}.{ind_meta['code']}..?startPeriod=2010&endPeriod=2026&format=jsondata"
        
        headers = {"User-Agent": "Mozilla/5.0"}
        try:
            r = requests.get(url, headers=headers, timeout=15)
            if r.status_code == 200:
                raw_data = r.json()
            else:
                raw_data = None
        except Exception:
            raw_data = None

    if raw_data and "dataSets" in raw_data and len(raw_data["dataSets"]) > 0:
        try:
            dataset = raw_data["dataSets"][0]
            series_data = dataset.get("series", {})
            
            # Ambil label waktu dari struktur dimensi OECD
            time_dim = raw_data["structure"]["dimensions"]["observation"]
            time_labels = []
            for dim in time_dim:
                if dim.get("id") == "TIME_PERIOD" or "values" in dim:
                    time_labels = [v["id"] for v in dim["values"]]
                    break

            records = []
            for key, series_val in series_data.items():
                observations = series_val.get("observations", {})
                for time_idx_str, val_list in observations.items():
                    t_idx = int(time_idx_str)
                    if t_idx < len(time_labels):
                        period_val = time_labels[t_idx]
                        numeric_val = val_list[0]
                        records.append({
                            "Periode": period_val,
                            "Nilai": numeric_val
                        })

            if records:
                df_res = pd.DataFrame(records).sort_values("Periode")
                
                st.success(f"Berhasil memuat data untuk **{selected_country_name}** - **{selected_ind_name}**")
                
                # Visualisasi Grafik
                fig = go.Figure()
                fig.add_trace(go.Scatter(
                    x=df_res["Periode"],
                    y=df_res["Nilai"],
                    mode="lines+markers",
                    name=selected_country_name,
                    line=dict(width=2.5, color="#1f77b4")
                ))
                fig.update_layout(
                    xaxis=dict(title="Periode"),
                    yaxis=dict(title=ind_meta["unit"]),
                    hovermode="x unified"
                )
                st.plotly_chart(fig, use_container_width=True)

                # Tabel Data
                st.subheader("📋 Tabel Data Observasi")
                st.dataframe(df_res, use_container_width=True)
            else:
                st.warning("Struktur data terbaca, namun nilai observasi kosong untuk kombinasi ini.")
        except Exception as e:
            st.error(f"Terjadi kesalahan saat memproses data: {e}")
    else:
        # Fallback jika struktur tabel utama belum merangkum negara tersebut
        st.warning(
            f"Server OECD belum menyediakan data rilis terbuka untuk kombinasi **{selected_country_name}** "
            f"pada indikator **{selected_ind_name}** melalui jalur API publik ini. "
            "Coba pilih indikator atau negara lain (seperti Amerika Serikat atau Jepang)."
        )
