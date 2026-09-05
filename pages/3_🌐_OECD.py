import io
import pandas as pd
import plotly.graph_objects as go
import requests
import streamlit as st

st.set_page_config(page_title="OECD Live Data - Indonesia", layout="wide")

st.title("🌐 Portal Data OECD (Live SDMX API)")
st.write(
    "Data ekonomi makro Indonesia yang ditarik **secara langsung (*real-time*)** "
    "dari server resmi **OECD Data Explorer**."
)

# Indikator utama OECD yang memiliki endpoint live terbuka untuk Indonesia (IDN)
OECD_LIVE_SERIES = {
    "Real GDP Growth Rate": "DP_LIVE/IDN.GDV_ANNPCT.TOT.A",
    "Consumer Price Index Inflation": "DP_LIVE/IDN.CPI.TOTL.AGGY.GY",
    "Unemployment Rate": "DP_LIVE/IDN.UNE_RT.TOT.PER.A",
    "General Government Debt (% of GDP)": "DP_LIVE/IDN.GG_DEBT.PP_GDP.A"
}

st.subheader("1. Pilih Indikator Resmi OECD")
selected_name = st.selectbox("Pilih Seri Indikator Live:", list(OECD_LIVE_SERIES.keys()))
series_path = OECD_LIVE_SERIES[selected_name]

if st.button("🌐 Tarik Data Live dari OECD", type="primary"):
    with st.spinner(f"Menghubungkan ke server OECD untuk {selected_name}..."):
        # Endpoint SDMX JSON resmi OECD
        url = f"https://stats.oecd.org/SDMX-JSON/data/{series_path}/OECD?startTime=2010&endTime=2026"
        headers = {"User-Agent": "Mozilla/5.0"}
        
        try:
            r = requests.get(url, headers=headers, timeout=20)
            if r.status_code == 200:
                raw_data = r.json()
            else:
                raw_data = None
        except Exception as e:
            raw_data = None
            st.error(f"Gagal terhubung ke jaringan OECD: {e}")

    if raw_data and "dataSets" in raw_data and len(raw_data["dataSets"]) > 0:
        try:
            dataset = raw_data["dataSets"][0]
            series_data = dataset.get("series", {})
            
            # Ekstraksi label waktu (tahun) dari struktur metadata OECD
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
                        numeric_val = val_list[0] # Nilai data asli dari server OECD
                        records.append({
                            "Tahun": str(period_val),
                            "Nilai": float(numeric_val)
                        })

            if records:
                df_res = pd.DataFrame(records).sort_values("Tahun")
                
                st.success(f"Berhasil menarik data *live* dari OECD untuk **{selected_name}**")
                
                # Visualisasi Grafik Interaktif
                fig = go.Figure()
                fig.add_trace(go.Scatter(
                    x=df_res["Tahun"],
                    y=df_res["Nilai"],
                    mode="lines+markers",
                    name="Indonesia (OECD Live)",
                    line=dict(width=2.5, color="#1f77b4"),
                    hovertemplate="Tahun %{x}<br>Nilai: %{y}<extra></extra>"
                ))
                fig.update_layout(
                    xaxis=dict(title="Tahun", tickmode="linear"),
                    yaxis=dict(title="Nilai Indikator"),
                    hovermode="x unified",
                    margin=dict(l=20, r=20, t=40, b=20)
                )
                st.plotly_chart(fig, use_container_width=True)

                # Tabel Data & Ekspor
                st.subheader("📋 Tabel Data Observasi Live")
                c_csv, c_xlsx = st.columns(2)
                
                c_csv.download_button(
                    "📥 Unduh CSV",
                    df_res.to_csv(index=False).encode("utf-8"),
                    f"OECD_Live_{selected_name.replace(' ', '_')}.csv",
                    "text/csv"
                )

                buf = io.BytesIO()
                with pd.ExcelWriter(buf, engine="openpyxl") as writer:
                    df_res.to_excel(writer, index=False, sheet_name="OECD Live Data")
                c_xlsx.download_button(
                    "📊 Unduh Excel (.xlsx)",
                    buf.getvalue(),
                    f"OECD_Live_{selected_name.replace(' ', '_')}.xlsx",
                    "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                )

                st.dataframe(df_res, use_container_width=True)
                st.caption("🔗 Sumber: Diambil secara real-time langsung dari API resmi OECD Data Explorer.")
            else:
                st.warning("Struktur respons API OECD terbaca, tetapi nilai observasi kosong untuk parameter ini.")
        except Exception as err:
            st.error(f"Terjadi kesalahan saat memproses format data OECD: {err}")
    else:
        st.warning(
            "Server OECD belum membuka akses deret waktu *live* untuk indikator ini pada wilayah Indonesia. "
            "Silakan coba pilih indikator makro utama lainnya di daftar atas."
        )
