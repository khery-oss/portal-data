import io
import pandas as pd
import plotly.graph_objects as go
import requests
import streamlit as st

st.set_page_config(page_title="Climate & Environment Explorer - Indonesia", layout="wide")

st.title("🌿 Climate & Environment - Indonesia")
st.markdown(
    "Eksplorasi indikator iklim, lingkungan hidup, dan keberlanjutan Indonesia dari "
    "**World Bank World Development Indicators** — *100% Live API*. "
    "Data mencakup emisi karbon, curah hujan, deforestasi, energi, bencana alam, dan kualitas udara."
)

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
}

# =============================================================================
# LOAD KATALOG INDIKATOR IKLIM & LINGKUNGAN — 100% LIVE API
# Filter dari WDI menggunakan keyword iklim/lingkungan
# =============================================================================
@st.cache_data(ttl=86400, show_spinner=False)
def load_climate_indicators():
    indicators = []
    url = "https://api.worldbank.org/v2/indicator?source=2&format=json&per_page=3000"
    try:
        res = requests.get(url, headers=HEADERS, timeout=25)
        if res.status_code != 200:
            return []
        data = res.json()
        if len(data) > 1 and data[1]:
            climate_keywords = [
                "emission", "co2", "carbon", "greenhouse", "methane", "nitrous",
                "forest", "deforest", "tree", "land", "soil",
                "precipitation", "rainfall", "temperature", "climate",
                "disaster", "flood", "drought", "hazard",
                "renewable", "energy", "electricity", "fossil", "coal", "oil", "gas",
                "pollution", "particulate", "air quality", "pm2",
                "water", "freshwater", "ocean", "marine",
                "biodiversity", "species", "protected area",
                "waste", "recycl", "sanitation",
                "environment", "ecological", "sustainability",
            ]
            for item in data[1]:
                ind_id = item.get("id", "")
                ind_name = item.get("name", "")
                if ind_id and ind_name and any(
                    kw in ind_name.lower() or kw in ind_id.lower()
                    for kw in climate_keywords
                ):
                    indicators.append({
                        "id": ind_id,
                        "name": ind_name,
                        "sourceNote": item.get("sourceNote", ""),
                        "sourceOrg": item.get("sourceOrganization", "World Bank")
                    })
    except Exception:
        pass
    return indicators

with st.spinner("Menghubungkan ke katalog indikator iklim & lingkungan..."):
    climate_indicators = load_climate_indicators()

if not climate_indicators:
    st.error("Gagal memuat katalog indikator. Periksa koneksi internet.")
    st.stop()

# =============================================================================
# PENCARIAN INDIKATOR
# =============================================================================
st.subheader("1. Pencarian Indikator")

st.caption(
    f"Katalog berisi **{len(climate_indicators)}** indikator iklim & lingkungan dari World Bank WDI. "
    "Ketik kata kunci untuk mencari."
)

query = st.text_input(
    "🔍 Cari indikator iklim & lingkungan (Bahasa Inggris):",
    placeholder="Contoh: co2 · emission · forest · precipitation · renewable · disaster · flood · temperature",
    value=""
).strip()

if not query:
    st.info(
        "Ketik kata kunci untuk mencari. Contoh: "
        "**co2**, **emission**, **forest**, **precipitation**, **renewable energy**, "
        "**disaster**, **flood**, **temperature**, **pollution**, **water**."
    )
    st.stop()

tokens = query.lower().split()
results = [
    ind for ind in climate_indicators
    if any(t in ind["name"].lower() or t in ind["id"].lower() for t in tokens)
]
results = sorted(results, key=lambda x: (len(x["name"]), x["name"]))

if not results:
    st.warning(f"Tidak ditemukan indikator untuk kata kunci **'{query}'**. Coba kata kunci lain.")
    st.stop()

st.success(f"Ditemukan **{len(results)}** indikator untuk kata kunci **'{query}'**.")

# =============================================================================
# PILIH INDIKATOR
# =============================================================================
selected_ind = st.selectbox(
    "Pilih Indikator:",
    options=results,
    format_func=lambda item: item["name"]
)

kode_indikator = selected_ind["id"]
link_resmi = f"https://data.worldbank.org/indicator/{kode_indikator}?locations=ID"

with st.expander("ℹ️ Definisi & Metadata Resmi", expanded=False):
    st.markdown(f"**Kode Indikator:** `{kode_indikator}`")
    st.markdown(f"**Organisasi Sumber:** {selected_ind['sourceOrg']}")
    note = selected_ind.get("sourceNote", "")
    st.markdown(f"**Definisi:** {note if note else 'Tidak ada deskripsi rinci.'}")
    st.markdown(f"🔗 [Lihat di World Bank]({link_resmi})")

# =============================================================================
# PENARIKAN DATA INDONESIA — 100% LIVE
# =============================================================================
st.subheader("2. Penarikan Data Indonesia")

if st.button("📊 Ambil Data Indonesia", type="primary"):
    with st.spinner(f"Mengunduh data untuk '{selected_ind['name']}'..."):
        data_url = (
            f"https://api.worldbank.org/v2/country/IDN/indicator/{kode_indikator}"
            f"?format=json&per_page=1000"
        )
        try:
            r = requests.get(data_url, headers=HEADERS, timeout=20)

            if r.status_code != 200:
                st.error(f"Gagal menghubungi server World Bank (HTTP {r.status_code}).")
                st.stop()

            data_json = r.json()
            records = []

            if len(data_json) > 1 and data_json[1]:
                for item in data_json[1]:
                    thn = item.get("date")
                    val = item.get("value")
                    if thn is not None and val is not None:
                        try:
                            records.append({
                                "Tahun": int(thn),
                                "nilai_raw": round(float(val), 4)
                            })
                        except (ValueError, TypeError):
                            continue

            if not records:
                st.warning(
                    f"Indikator **'{selected_ind['name']}'** terdaftar di World Bank "
                    "namun data untuk Indonesia belum tersedia. Silakan pilih indikator lain."
                )
                st.stop()

            # Deteksi unit dari nama indikator
            name_lower = selected_ind["name"].lower()
            if "kt" in name_lower and ("co2" in name_lower or "emission" in name_lower):
                unit = "kt CO2"
            elif "metric tons per capita" in name_lower:
                unit = "Ton per Kapita"
            elif "% of gdp" in name_lower:
                unit = "% of GDP"
            elif "% of total" in name_lower or "% of land" in name_lower:
                unit = "%"
            elif "%" in selected_ind["name"]:
                unit = "%"
            elif "mm per year" in name_lower or "mm" in name_lower:
                unit = "mm/tahun"
            elif "kwh" in name_lower:
                unit = "kWh"
            elif "mw" in name_lower:
                unit = "MW"
            elif "hectare" in name_lower or "sq. km" in name_lower:
                unit = "Hektar/km²"
            elif "per capita" in name_lower:
                unit = "Per Kapita"
            elif "index" in name_lower:
                unit = "Index"
            elif "million" in name_lower:
                unit = "Juta"
            else:
                unit = "Nilai"

            val_col = f"Nilai ({unit})"
            df = (
                pd.DataFrame(records)
                .groupby("Tahun", as_index=False)["nilai_raw"]
                .mean()
                .round(4)
                .rename(columns={"nilai_raw": val_col})
                .sort_values(by="Tahun", ascending=True)
            )

            st.success(f"Berhasil menarik **{len(df)}** observasi tahunan untuk Indonesia!")
            st.divider()

            st.markdown(f"🔗 **Halaman Resmi World Bank:** [{selected_ind['name']}]({link_resmi})")

            # Tombol Download
            col1, col2 = st.columns(2)
            col1.download_button(
                "📥 Unduh CSV",
                df.to_csv(index=False).encode("utf-8"),
                f"Climate_IDN_{kode_indikator}.csv",
                "text/csv"
            )
            buffer = io.BytesIO()
            with pd.ExcelWriter(buffer, engine="openpyxl") as writer:
                df.to_excel(writer, index=False, sheet_name="Climate Data")
            col2.download_button(
                "📊 Unduh Excel (.xlsx)",
                buffer.getvalue(),
                f"Climate_IDN_{kode_indikator}.xlsx",
                "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            )

            # Warna chart berdasarkan jenis indikator
            name_l = selected_ind["name"].lower()
            if any(k in name_l for k in ["co2", "emission", "carbon", "greenhouse", "methane"]):
                color = "#d62728"  # merah — emisi berbahaya
            elif any(k in name_l for k in ["forest", "tree", "biodiversity", "protected"]):
                color = "#2ca02c"  # hijau — lingkungan hidup
            elif any(k in name_l for k in ["renewable", "solar", "wind", "hydro"]):
                color = "#17becf"  # biru muda — energi bersih
            elif any(k in name_l for k in ["precipitation", "rainfall", "water", "flood"]):
                color = "#1f77b4"  # biru — air
            elif any(k in name_l for k in ["disaster", "hazard", "drought"]):
                color = "#ff7f0e"  # oranye — bencana
            else:
                color = "#7f7f7f"  # abu — lainnya

            fig = go.Figure()
            fig.add_trace(go.Scatter(
                x=df["Tahun"],
                y=df[val_col],
                mode="lines+markers",
                name="Indonesia",
                line=dict(width=2.5, color=color),
                marker=dict(size=7),
                hovertemplate=f"Tahun %{{x}}<br>Nilai: %{{y:,.4f}} {unit}<extra></extra>"
            ))
            fig.update_layout(
                xaxis=dict(title="Tahun", tickmode="linear"),
                yaxis=dict(title=unit),
                hovermode="x unified",
                margin=dict(l=20, r=20, t=30, b=20)
            )
            st.plotly_chart(fig, use_container_width=True)

            with st.expander("📋 Tabel Data Lengkap"):
                st.dataframe(
                    df.sort_values(by="Tahun", ascending=False),
                    use_container_width=True
                )

        except Exception as e:
            st.error(f"Gagal mengambil data: {e}")
