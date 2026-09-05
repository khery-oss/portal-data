import io
import pandas as pd
import plotly.graph_objects as go
import requests
import streamlit as st

st.set_page_config(page_title="UN Data Explorer - Indonesia", layout="wide")

st.title("🇺🇳 United Nations (UN) SDG - Portal Data Indonesia")
st.write(
    "Eksplorasi indikator resmi pembangunan berkelanjutan dan sosio-ekonomi dari **United Nations Statistics Division (UNSD API)** "
    "khusus untuk **Indonesia (M49 Code: 360)** secara langsung (*100% real-time live API*)."
)

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Accept": "application/json"
}

# DAFTAR SERI UTAMA UNSD SDG YANG TERSEDIA LENGKAP UNTUK INDONESIA
UN_SDG_SERIES = {
    "Income Share Held by Bottom 40% of Population (%)": {
        "code": "SI_DST_040P", "goal": "Goal 10: Penurunan Kesenjangan", "unit": "%",
        "desc": "Pangsa persentase pendapatan atau konsumsi nasional yang dinikmati oleh 40% populasi terbawah."
    },
    "Annual Growth Rate of Real GDP per Employed Person (%)": {
        "code": "SL_EMP_PCAP", "goal": "Goal 8: Pekerjaan Layak & Pertumbuhan", "unit": "%",
        "desc": "Laju pertumbuhan tahunan PDB riil per tenaga kerja yang bekerja (produktivitas tenaga kerja)."
    },
    "Annual Growth Rate of Real GDP per Capita (%)": {
        "code": "NY_GDP_PCAP", "goal": "Goal 8: Pekerjaan Layak & Pertumbuhan", "unit": "%",
        "desc": "Laju pertumbuhan tahunan Produk Domestik Bruto riil per kapita."
    },
    "Unemployment Rate (% of Total Labor Force)": {
        "code": "SL_TLF_UEM", "goal": "Goal 8: Pekerjaan Layak & Pertumbuhan", "unit": "%",
        "desc": "Tingkat pengangguran terbuka nasional resmi berdasarkan pemantauan ILO/PBB."
    },
    "Manufacturing Value Added as Proportion of GDP (%)": {
        "code": "NV_IND_MANF", "goal": "Goal 9: Industri & Inovasi", "unit": "% of GDP",
        "desc": "Nilai tambah sektor industri manufaktur sebagai proporsi dari total PDB nasional."
    },
    "Renewable Energy Share in Total Final Energy Consumption (%)": {
        "code": "EG_FEC_RNEW", "goal": "Goal 7: Energi Bersih", "unit": "%",
        "desc": "Pangsa energi baru terbarukan dalam total konsumsi energi nasional."
    },
    "Carbon Dioxide Emissions per Unit of Value Added (kg CO2)": {
        "code": "EN_ATM_CO2MVA", "goal": "Goal 9: Industri & Inovasi", "unit": "kg CO2 / USD",
        "desc": "Intensitas emisi karbon dioksida per unit nilai tambah manufaktur."
    },
    "Proportion of Population Below International Poverty Line (%)": {
        "code": "SI_POV_DAY1", "goal": "Goal 1: Pengentasan Kemiskinan", "unit": "%",
        "desc": "Persentase penduduk yang hidup di bawah garis kemiskinan ekstrem internasional."
    }
}

# 1. Pemilihan Indikator
st.subheader("1. Pemilihan Indikator Sosio-Ekonomi")
col_goal, col_ind = st.columns([1.2, 2])

daftar_goal = sorted(list(set(v["goal"] for v in UN_SDG_SERIES.values())))
with col_goal:
    pilihan_goal = st.selectbox("Pilar Target SDGs:", ["Semua Target"] + daftar_goal)

opsi = [
    k for k, v in UN_SDG_SERIES.items()
    if pilihan_goal == "Semua Target" or v["goal"] == pilihan_goal
]

with col_ind:
    selected_name = st.selectbox("Pilih Indikator:", opsi)

meta = UN_SDG_SERIES[selected_name]
kode_series = meta["code"]

with st.expander("ℹ️ Metadata Resmi PBB (UNSD)", expanded=False):
    st.markdown(f"**Indikator:** {selected_name}")
    st.markdown(f"**Target SDG:** `{meta['goal']}`")
    st.markdown(f"**UN Series Code:** `{kode_series}`")
    st.markdown(f"**Kode Negara PBB (M49):** `360 (Indonesia)`")
    st.markdown(f"**Definisi:**\n{meta['desc']}")
    st.markdown("🔗 **Portal Sumber:** [UNSD Global SDG Database](https://unstats.un.org/sdgs/dataportal)")

# 2. Penarikan Data Runtun Waktu
st.subheader("2. Penarikan Data Runtun Waktu")

if st.button("📊 Ambil Data PBB Indonesia", type="primary"):
    with st.spinner(f"Menghubungi endpoint resmi PBB untuk seri {kode_series}..."):
        # Endpoint query resmi yang dipakai oleh UI web unstats.un.org
        api_url = f"https://unstats.un.org/sdgapi/v1/sdg/Series/Data?seriesCode={kode_series}&areaCode=360&pageSize=500"
        records = []
        
        try:
            res = requests.get(api_url, headers=HEADERS, timeout=25)
            
            # Jika request pertama ditolak, gunakan parameter geoAreaCode
            if res.status_code != 200 or not res.json().get("data"):
                alt_url = f"https://unstats.un.org/sdgapi/v1/sdg/Series/Data?seriesCode={kode_series}&geoAreaCode=360&pageSize=500"
                res = requests.get(alt_url, headers=HEADERS, timeout=25)
                
            if res.status_code == 200:
                payload = res.json()
                data_list = payload.get("data", [])
                
                for row in data_list:
                    thn = row.get("timePeriodStart") or row.get("timePeriod")
                    val = row.get("value")
                    
                    if thn is not None and val is not None:
                        try:
                            clean_thn = int(str(thn)[:4])
                            clean_val = float(str(val).replace("<", "").replace(">", "").strip())
                            records.append({
                                "Tahun": clean_thn,
                                f"Nilai ({meta['unit']})": clean_val
                            })
                        except (ValueError, TypeError):
                            continue

            if records:
                val_col = f"Nilai ({meta['unit']})"
                # Group by Tahun untuk menangani jika ada breakdown gender/wilayah pada tahun yang sama
                df_un = (
                    pd.DataFrame(records)
                    .groupby("Tahun", as_index=False)[val_col]
                    .mean()
                    .round(2)
                    .sort_values(by="Tahun", ascending=True)
                )

                st.success(f"Berhasil menarik {len(df_un)} observasi data langsung dari server PBB!")
                st.divider()

                # Tombol Download Data
                c1, c2 = st.columns(2)
                c1.download_button(
                    "📥 Unduh CSV",
                    df_un.to_csv(index=False).encode("utf-8"),
                    f"UN_SDG_{kode_series}_IDN.csv",
                    "text/csv"
                )
                buf = io.BytesIO()
                with pd.ExcelWriter(buf, engine="openpyxl") as writer:
                    df_un.to_excel(writer, index=False, sheet_name="UN Data")
                c2.download_button(
                    "📊 Unduh Excel (.xlsx)",
                    buf.getvalue(),
                    f"UN_SDG_{kode_series}_IDN.xlsx",
                    "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                )

                # Plotly Visualisasi Interaktif
                fig = go.Figure()
                fig.add_trace(go.Scatter(
                    x=df_un["Tahun"],
                    y=df_un[val_col],
                    mode="lines+markers",
                    name="Indonesia (UN SDGs)",
                    line=dict(width=2.5, color="#009edb"),
                    hovertemplate=f"Tahun %{{x}}<br>Nilai: %{{y}} {meta['unit']}<extra></extra>"
                ))
                fig.update_layout(
                    xaxis=dict(title="Tahun", tickmode="linear"),
                    yaxis=dict(title=meta["unit"]),
                    hovermode="x unified",
                    margin=dict(l=20, r=20, t=40, b=20)
                )
                st.plotly_chart(fig, use_container_width=True)

                with st.expander("📋 Tabel Runtun Waktu Lengkap"):
                    st.dataframe(df_un.sort_values(by="Tahun", ascending=False), use_container_width=True)
            else:
                st.warning("Observasi runtun waktu untuk indikator ini belum dilaporkan atau sedang dalam proses pembaruan di server PBB.")
        except Exception as e:
            st.error(f"Gagal menghubungi server PBB: {e}")
