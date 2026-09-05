import io
import pandas as pd
import plotly.graph_objects as go
import requests
import streamlit as st

st.set_page_config(page_title="OECD Data Explorer - Live API", layout="wide")

st.title("🌐 Portal Data OECD (Live SDMX API)")
st.write(
    "Eksplorasi data makroekonomi, sosial, dan indikator pembangunan internasional "
    "langsung dari server resmi **OECD (Organization for Economic Cooperation and Development)**."
)

@st.cache_data(ttl=3600)
def fetch_oecd_data(country="IDN", indicator="CPI"):
    url = f"https://stats.oecd.org/SDMX-JSON/data/DP_LIVE/{country}.{indicator}.ALL/OECD?startTime=2010&endTime=2026"
    headers = {"User-Agent": "Mozilla/5.0"}
    try:
        r = requests.get(url, headers=headers, timeout=15)
        if r.status_code == 200:
            return r.json()
    except Exception:
        pass
    return None

st.subheader("1. Pilih Indikator Global OECD")
ind_choice = st.selectbox(
    "Pilih Seri Data:",
    [
        "Consumer Price Index (Inflation)", 
        "Gross Domestic Product (GDP Growth)", 
        "Unemployment Rate",
        "General Government Debt"
    ]
)

ind_map = {
    "Consumer Price Index (Inflation)": "CPI",
    "Gross Domestic Product (GDP Growth)": "GDV_ANNPCT",
    "Unemployment Rate": "UNE_RT",
    "General Government Debt": "GG_DEBT"
}

target_ind = ind_map[ind_choice]

country_code = st.selectbox("Pilih Negara / Ekonomi:", ["IDN (Indonesia)", "USA (Amerika Serikat)", "JPN (Jepang)", "DEU (Jerman)", "GBR (Inggris)"], index=0)
iso_c = country_code.split(" ")[0]

if st.button("🌐 Tarik Data OECD Live", type="primary"):
    with st.spinner(f"Menghubungkan ke server OECD untuk {ind_choice} ({iso_c})..."):
        raw_data = fetch_oecd_data(country=iso_c, indicator=target_ind)

    if raw_data and "dataSets" in raw_data and len(raw_data["dataSets"]) > 0:
        try:
            dataset = raw_data["dataSets"][0]
            series_data = dataset.get("series", {})
            
            time_points = raw_data["structure"]["dimensions"]["observation"][0]["values"]
            time_labels = [tp["id"] for tp in time_points]

            records = []
            for key, series_val in series_data.items():
                observations = series_val.get("observations", {})
                for time_idx_str, val_list in observations.items():
                    t_idx = int(time_idx_str)
                    if t_idx < len(time_labels):
                        year_val = time_labels[t_idx]
                        numeric_val = val_list[0]
                        records.append({
                            "Periode": year_val,
                            "Nilai": numeric_val
                        })

            if records:
                df_res = pd.DataFrame(records).sort_values("Periode")
                
                st.success(f"Berhasil menarik data OECD untuk **{country_code}** - **{ind_choice}**")
                
                fig = go.Figure()
                fig.add_trace(go.Scatter(
                    x=df_res["Periode"],
                    y=df_res["Nilai"],
                    mode="lines+markers",
                    name=iso_c,
                    line=dict(width=2.5, color="#2ca02c")
                ))
                fig.update_layout(
                    xaxis=dict(title="Periode / Tahun"),
                    yaxis=dict(title="Nilai Indikator"),
                    hovermode="x unified"
                )
                st.plotly_chart(fig, use_container_width=True)

                st.subheader("📋 Tabel Data Observasi")
                st.dataframe(df_res, use_container_width=True)
            else:
                st.warning("Struktur data ditemukan, tetapi isi observasi kosong untuk parameter ini.")
        except Exception as e:
            st.error(f"Kesalahan parsing data OECD: {e}")
    else:
        st.warning(
            f"Server OECD tidak mengembalikan data untuk kombinasi negara `{iso_c}` dan indikator `{target_ind}`."
        )
