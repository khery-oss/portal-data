import io
import pandas as pd
import plotly.graph_objects as go
import requests
import streamlit as st

st.set_page_config(page_title="WHO Explorer - IndoEcon", layout="wide")

st.title("🏥 WHO (World Health Organization) - Modal Manusia & Kesehatan")
st.markdown(
    "Eksplorasi indikator kesehatan publik dan modal manusia khusus wilayah **Indonesia (IDN)** "
    "langsung dari **WHO Global Health Observatory (GHO) API** secara *real-time* (*100% Live API Dinamis*)."
)

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
}

# =============================================================================
# 1. TARIK HANYA INDIKATOR YANG MEMILIKI DATA INDONESIA (IDN)
# =============================================================================
@st.cache_data(ttl=86400, show_spinner=False)
def get_indonesia_active_indicators():
    try:
        # Mengambil langsung data khusus wilayah IDN dari endpoint GHO
        res = requests.get("https://ghoapi.azureedge.net/api/Indicator?$filter=SpatialDim eq 'IDN'", headers=HEADERS, timeout=25)
        if res.status_code == 200:
            data = res.json().get("value", [])
            mapping = {}
            for item in data:
                # OData GHO mengembalikan entri berdasarkan observasi wilayah
                code = item.get("IndicatorCode") or item.get("Indicator")
                name = item.get("IndicatorName")
                if code and name:
                    mapping[name] = code
            return mapping
    except Exception:
        pass
    return {}

with st.spinner("Memindai dan menyaring indikator yang memiliki data resmi untuk Indonesia di server WHO..."):
    indicator_dict = get_indonesia_active_indicators()

# Fallback jika endpoint spesifik kosong, gunakan direktori utama yang sudah dikurasi
if not indicator_dict:
    indicator_dict = {
        "Life expectancy at birth (years)": "WHOSIS_000001",
        "Healthy life expectancy (HALE) at birth (years)": "WHOSIS_000002",
        "Under-five mortality rate (probability of dying by age 5 per 1,000 live births)": "MDG_0000000007",
        "Infant mortality rate (probability of dying between birth and exact age 1 per 1,000 live births)": "MDG_0000000001",
        "Neonatal mortality rate (per 1,000 live births)": "WHOSIS_000003",
        "Maternal mortality ratio (per 100,000 live births)": "MDG_0000000026",
        "Stunting prevalence among children under 5 years (%)": "NUTRITION_STUNTING_PREV",
        "Wasting prevalence among children under 5 years (%)": "NUTRITION_WASTING_PREV",
        "UHC service coverage index": "UHC_INDEX_REPORTED",
        "Medical doctors (per 10,000 population)": "HWF_0001",
        "Nursing and midwifery personnel (per 10,000 population)": "HWF_0002",
        "Hospital beds (per 10,000 population)": "HWF_BE_HOSP"
    }

st.subheader("1. Pemilihan Indikator Khusus Indonesia")

search_term = st.text_input("🔍 Cari Indikator (ketik kata kunci, misal: Life Expectancy, Mortality, Stunting, Doctor):", "")

filtered_options = [
    name for name in indicator_dict.keys()
    if not search_term.strip() or search_term.lower() in name.lower()
]

if not filtered_options:
    st.warning("Tidak ditemukan indikator yang cocok dengan kata kunci tersebut.")
    st.stop()

selected_indicator_name = st.selectbox(
    f"Pilih dari {len(filtered_options)} Indikator Tersedia untuk Indonesia:",
    filtered_options
)

selected_code = indicator_dict[selected_indicator_name]

with st.expander("ℹ️ Metadata Resmi WHO GHO", expanded=False):
    st.markdown(f"**Nama Indikator:** {selected_indicator_name}")
    st.markdown(f"**Kode Seri GHO API:** `{selected_code}`")
    st.markdown(f"**Cakupan Geografis:** Indonesia (`IDN`)")
    st.markdown("🔗 **Sumber Resmi:** [WHO Global Health Observatory](https://www.who.int/data/gho)")

# =============================================================================
# 2. PENARIKAN DATA RUN TUN WAKTU INDONESIA
# =============================================================================
st.subheader("2. Penarikan Data Runtun Waktu Nasional (Indonesia)")

if st.button("📊 Ambil Data WHO (Live API)", type="primary"):
    with st.spinner(f"Menarik data runtun waktu untuk '{selected_indicator_name}'..."):
        api_url = f"https://ghoapi.azureedge.net/api/{selected_code}"
        query_params = {"$filter": "SpatialDim eq 'IDN'"}

        try:
            res = requests.get(api_url, params=query_params, headers=HEADERS, timeout=25)
            
            if res.status_code == 200:
                payload = res.json()
                items = payload.get("value", [])

                records = []
                for it in items:
                    th = it.get("TimeDim")
                    val = it.get("NumericValue")
                    
                    dim1 = it.get("Dim1")
                    if dim1 and dim1 not in ["BTSX", "TOTAL", "SEX_BTSX"]:
                        continue

                    if th is not None and val is not None:
                        try:
                            records.append({
                                "Tahun": int(th),
                                "Nilai": round(float(val), 2)
                            })
                        except (ValueError, TypeError):
                            continue

                if not records and items:
                    for it in items:
                        th = it.get("TimeDim")
                        val = it.get("NumericValue")
                        if th is not None and val is not None:
                            try:
                                records.append({"Tahun": int(th), "Nilai": round(float(val), 2)})
                            except (ValueError, TypeError):
                                continue

                if records:
                    df_raw = pd.DataFrame(records)
                    df_who = df_raw.groupby("Tahun", as_index=False)["Nilai"].mean().round(2)
                    df_who = df_who.sort_values(by="Tahun", ascending=True)

                    st.success(f"Berhasil menarik {len(df_who)} observasi tahunan resmi untuk Indonesia dari server WHO!")
                    st.divider()

                    # Tombol Unduh Berkas
                    c1, c2 = st.columns(2)
                    c1.download_button(
                        "📥 Unduh CSV",
                        df_who.to_csv(index=False).encode("utf-8"),
                        f"WHO_Indonesia_{selected_code}.csv",
                        "text/csv"
                    )
                    buf = io.BytesIO()
                    with pd.ExcelWriter(buf, engine="openpyxl") as writer:
                        df_who.to_excel(writer, index=False, sheet_name="WHO Indonesia")
                    c2.download_button(
                        "📊 Unduh Excel (.xlsx)",
                        buf.getvalue(),
                        f"WHO_Indonesia_{selected_code}.xlsx",
                        "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                    )

                    # Visualisasi Plotly Interaktif
                    fig = go.Figure()
                    fig.add_trace(go.Scatter(
                        x=df_who["Tahun"],
                        y=df_who["Nilai"],
                        mode="lines+markers",
                        name="Indonesia (WHO GHO)",
                        line=dict(width=2.8, color="#0093D5"),
                        marker=dict(size=7),
                        hovertemplate="Tahun %{x}<br>Nilai: %{y:,.2f}<extra></extra>"
                    ))
                    fig.update_layout(
                        xaxis=dict(title="Tahun", tickmode="linear"),
                        yaxis=dict(title="Nilai Indikator"),
                        hovermode="x unified",
                        margin=dict(l=20, r=20, t=30, b=20)
                    )
                    st.plotly_chart(fig, use_container_width=True)

                    with st.expander("📋 Tabel Runtun Waktu Lengkap"):
                        st.dataframe(df_who.sort_values(by="Tahun", ascending=False), use_container_width=True)
                else:
                    st.warning("Server WHO merespons, namun catatan observasi runtun waktu untuk Indonesia belum tersedia pada indikator ini.")
            else:
                st.error(f"Gagal menghubungi server WHO (Kode Status HTTP: {res.status_code}).")
        except Exception as e:
            st.error(f"Terjadi kesalahan saat memproses data WHO: {e}")
