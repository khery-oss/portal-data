import io
import pandas as pd
import plotly.graph_objects as go
import requests
import streamlit as st

st.set_page_config(page_title="World Bank - Portal Data", layout="wide")
st.title("🌐 Database Lengkap World Bank - Indonesia")

HEADERS = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}

@st.cache_data(ttl=86400)
def load_wb_indicators():
    indicators = []
    url = "https://api.worldbank.org/v2/indicator?format=json&per_page=5000"
    try:
        res = requests.get(url, headers=HEADERS, timeout=25)
        data = res.json()
        if len(data) > 1 and data[1]:
            for item in data[1]:
                ind_id = item.get("id")
                ind_name = item.get("name")
                if ind_id and ind_name and not ind_id.startswith("6.") and not ind_id.startswith("7."):
                    indicators.append({
                        "id": ind_id,
                        "name": ind_name,
                        "sourceNote": item.get("sourceNote", ""),
                        "sourceOrg": item.get("sourceOrganization", "World Bank")
                    })
    except Exception:
        pass
    return indicators

all_wb_indicators = load_wb_indicators()

# Pilihan cepat indikator makro utama World Bank yang dijamin akurat kodenya untuk Indonesia
POPULAR_INDICATORS = {
    "-- Pilih Indikator Utama (Shortcut) --": "",
    "GDP growth (annual %)": "NY.GDP.MKTP.KD.ZG",
    "GDP (current US$)": "NY.GDP.MKTP.CD",
    "GDP per capita (current US$)": "NY.GDP.PCAP.CD",
    "Inflation, consumer prices (annual %)": "FP.CPI.TOTL.ZG",
    "Unemployment, total (% of total labor force)": "SL.UEM.TOTL.ZS",
    "Poverty headcount ratio at national poverty lines (% of population)": "SI.POV.NAHC",
    "Foreign direct investment, net inflows (% of GDP)": "BX.KLT.DINV.WD.GD.ZS",
    "CO2 emissions (kt)": "EN.ATM.CO2E.KT",
    "Population, total": "SP.POP.TOTL"
}

st.subheader("1. Pilih atau Cari Indikator")
selected_shortcut = st.selectbox("Pintasan Indikator Utama:", list(POPULAR_INDICATORS.keys()))

if selected_shortcut != "-- Pilih Indikator Utama (Shortcut) --":
    kode_wb = POPULAR_INDICATORS[selected_shortcut]
    selected_wb_label = selected_shortcut
    selected_wb = {"sourceOrg": "World Bank", "sourceNote": "Official World Bank development indicators database."}
else:
    query_wb = st.text_input(
        "Atau cari manual (ketik kata kunci persis, misal: 'GDP', 'Inflation'):",
        value=""
    ).strip()
    
    selected_wb_label = None
    kode_wb = None
    selected_wb = {}

    if query_wb and all_wb_indicators:
        results_wb = [
            ind for ind in all_wb_indicators
            if query_wb.lower() in ind["name"].lower()
        ]
        if results_wb:
            options_wb = {ind['name']: ind for ind in results_wb}
            selected_wb_label = st.selectbox("Hasil Pencarian:", list(options_wb.keys()))
            selected_wb = options_wb[selected_wb_label]
            kode_wb = selected_wb["id"]

# Jika indikator sudah dipilih baik dari shortcut maupun pencarian
if kode_wb:
    with st.expander("ℹ️ Definisi & Organisasi Sumber Data", expanded=False):
        st.markdown(f"**Indikator Terpilih:** {selected_wb_label}")
        st.markdown(f"**Kode Seri API:** `{kode_wb}`")
        st.markdown(f"**Organisasi Penyusun:** {selected_wb.get('sourceOrg', 'World Bank')}")
        st.markdown(f"**Definisi:** {selected_wb.get('sourceNote', 'Data resmi World Bank untuk Indonesia.')}")

    if st.button("📊 Ambil Data World Bank", type="primary"):
        with st.spinner(f"Menarik time-series untuk {selected_wb_label}..."):
            data_url = f"https://api.worldbank.org/v2/country/IDN/indicator/{kode_wb}?format=json&per_page=120"
            try:
                r_data = requests.get(data_url, headers=HEADERS, timeout=15)
                data_json = r_data.json()

                records_wb = []
                if len(data_json) > 1 and data_json[1]:
                    for item in data_json[1]:
                        thn = item.get("date")
                        val = item.get("value")
                        if val is not None:
                            try:
                                records_wb.append({"Tahun": int(thn), "Nilai": round(float(val), 2)})
                            except (ValueError, TypeError):
                                continue

                if records_wb:
                    df_wb = pd.DataFrame(records_wb).sort_values(by="Tahun", ascending=True)
                    link_wb = f"https://data.worldbank.org/indicator/{kode_wb}?locations=ID"

                    st.divider()
                    st.markdown(f"🔗 **Tautan Resmi World Bank:** [{selected_wb_label}]({link_wb})")

                    c1, c2 = st.columns(2)
                    c1.download_button(
                        "📥 Unduh CSV",
                        df_wb.to_csv(index=False).encode('utf-8'),
                        f"WB_{kode_wb}_IDN.csv",
                        "text/csv"
                    )
                    buf_wb = io.BytesIO()
                    with pd.ExcelWriter(buf_wb, engine='openpyxl') as writer:
                        df_wb.to_excel(writer, index=False, sheet_name="Data")
                    c2.download_button(
                        "📊 Unduh Excel (.xlsx)",
                        buf_wb.getvalue(),
                        f"WB_{kode_wb}_IDN.xlsx",
                        "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                    )

                    # Visualisasi Interaktif Plotly yang akurat
                    fig = go.Figure()
                    fig.add_trace(go.Scatter(
                        x=df_wb["Tahun"],
                        y=df_wb["Nilai"],
                        mode="lines+markers",
                        name="Indonesia (World Bank)",
                        line=dict(width=2.5, color="#002244"),
                        hovertemplate="Tahun %{x}<br>Nilai: %{y}<extra></extra>"
                    ))
                    fig.update_layout(
                        xaxis=dict(title="Tahun", tickmode="linear"),
                        yaxis=dict(title="Nilai Indikator"),
                        hovermode="x unified",
                        margin=dict(l=20, r=20, t=40, b=20)
                    )
                    st.plotly_chart(fig, use_container_width=True)

                    with st.expander("📋 Tabel Data Lengkap"):
                        st.dataframe(df_wb.sort_values(by="Tahun", ascending=False), use_container_width=True)
                else:
                    st.warning("Data runtun waktu untuk indikator ini tidak tersedia di server World Bank untuk Indonesia.")
            except Exception as e:
                st.error(f"Gagal memuat data: {e}")
