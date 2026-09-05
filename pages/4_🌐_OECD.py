import io
import pandas as pd
import plotly.graph_objects as go
import requests
import streamlit as st

st.set_page_config(page_title="OECD Data Indonesia - Live API", layout="wide")

st.title("🌐 Portal Data OECD (Fokus Indonesia)")
st.write(
    "Eksplorasi data makroekonomi dan indikator pembangunan **Indonesia** "
    "secara *real-time* langsung dari server resmi **OECD**."
)

# Indikator utama yang teruji memiliki ketersediaan data untuk Indonesia di OECD
OECD_IDN_INDICATORS = {
    "Gross Domestic Product (GDP Growth Rate)": {"path": "DP_LIVE/IDN.GDV_ANNPCT.TOT.A", "unit": "Persen (%)"},
    "Inflation Rate (CPI YoY)": {"path": "DP_LIVE/IDN.CPI.TOTL.AGGY.GY", "unit": "Persen (%)"},
    "Unemployment Rate": {"path": "DP_LIVE/IDN.UNE_RT.TOT.PER.A", "unit": "Persen (%)"},
    "General Government Debt (% of GDP)": {"path": "DP_LIVE/IDN.GG_DEBT.PP_GDP.A", "unit": "% dari PDB"}
}

st.subheader("1. Pilih Indikator OECD untuk Indonesia")
selected_ind_name = st.selectbox("Pilih Seri Indikator:", list(OECD_IDN_INDICATORS.keys()))
ind_meta = OECD_IDN_INDICATORS[selected_ind_name]

if st.button("🌐 Tarik Data OECD Live (Indonesia)", type="primary"):
    with st.spinner(f"Menarik data {selected_ind_name} untuk Indonesia..."):
        # Endpoint SDMX JSON OECD universal untuk ekonomi utama
        url = f"https://stats.oecd.org/SDMX-JSON/data/{ind_meta['path']}/OECD?startTime=2010&endTime=2026"
        
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
                
                st.success(f"Berhasil memuat data **Indonesia** - **{selected_ind_name}**")
                
                # Visualisasi Grafik
                fig = go.Figure()
                fig.add_trace(go.Scatter(
                    x=df_res["Periode"],
                    y=df_res["Nilai"],
                    mode="lines+markers",
                    name="Indonesia (OECD)",
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
                st.warning("Struktur data terbaca, namun nilai observasi kosong untuk indikator ini.")
        except Exception as e:
            st.error(f"Terjadi kesalahan saat memproses data: {e}")
    else:
        st.warning(
            f"Server OECD saat ini belum mempublikasikan deret waktu terbuka untuk indikator **{selected_ind_name}** "
            "khusus wilayah Indonesia melalui jalur API ini. Silakan coba indikator lainnya."
        )
