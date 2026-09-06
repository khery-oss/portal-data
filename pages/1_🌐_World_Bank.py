import io
import pandas as pd
import plotly.graph_objects as go
import requests
import streamlit as st

st.set_page_config(page_title="World Bank Data Explorer - Indonesia", layout="wide")

st.title("🌐 World Bank Open Data Explorer - Indonesia")
st.write(
    "Eksplorasi ribuan indikator resmi **World Bank (World Development Indicators)** "
    "khusus untuk Indonesia secara otomatis dan real-time."
)

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
}

# =============================================================================
# 1. LOAD KATALOG INDIKATOR — 100% LIVE DARI WDI API
# =============================================================================
@st.cache_data(ttl=86400, show_spinner=False)
def load_all_indicators():
    indicators = []
    url = "https://api.worldbank.org/v2/indicator?source=2&format=json&per_page=3000"
    try:
        res = requests.get(url, headers=HEADERS, timeout=25)
        if res.status_code != 200:
            return []
        data = res.json()
        if len(data) > 1 and data[1]:
            for item in data[1]:
                ind_id = item.get("id")
                ind_name = item.get("name")
                if ind_id and ind_name:
                    indicators.append({
                        "id": ind_id,
                        "name": ind_name,
                        "sourceNote": item.get("sourceNote", ""),
                        "sourceOrg": item.get("sourceOrganization", "World Bank")
                    })
    except Exception:
        pass
    return indicators

with st.spinner("Menghubungkan ke katalog World Development Indicators..."):
    all_indicators = load_all_indicators()

if not all_indicators:
    st.error("Gagal memuat katalog indikator. Periksa koneksi internet.")
    st.stop()

# =============================================================================
# 2. PENCARIAN BEBAS
# =============================================================================
st.subheader("1. Pencarian Indikator")

query = st.text_input(
    "🔍 Ketik kata kunci indikator (Bahasa Inggris):",
    placeholder="Contoh: gdp · inflation · poverty · unemployment · export · debt · mortality · enrollment",
    value=""
).strip()

if not query:
    st.info("Ketik kata kunci untuk mulai mencari indikator. Contoh: **gdp**, **inflation**, **poverty**, **unemployment**, **export**, **debt**.")
    st.stop()

query_tokens = query.lower().split()
results = [
    ind for ind in all_indicators
    if any(
        token in ind["name"].lower() or token in ind["id"].lower()
        for token in query_tokens
    )
]
results = sorted(results, key=lambda x: (len(x["name"]), x["name"]))

if not results:
    st.warning(f"Tidak ditemukan indikator untuk kata kunci **'{query}'**. Coba kata kunci lain.")
    st.stop()

st.success(f"Ditemukan **{len(results)}** indikator untuk kata kunci **'{query}'**.")

# =============================================================================
# 3. PILIH INDIKATOR
# =============================================================================
selected_ind = st.selectbox(
    "Pilih Indikator:",
    options=results,
    format_func=lambda item: item["name"]
)

kode_indikator = selected_ind["id"]
link_resmi = f"https://data.worldbank.org/indicator/{kode_indikator}?locations=ID"

with st.expander("ℹ️ Definisi & Metodologi Resmi", expanded=False):
    st.markdown(f"**Kode Indikator:** `{kode_indikator}`")
    st.markdown(f"**Organisasi Sumber:** {selected_ind['sourceOrg']}")
    note = selected_ind.get("sourceNote", "")
    st.markdown(f"**Definisi:** {note if note else 'Tidak ada deskripsi rinci.'}")
    st.markdown(f"🔗 [Lihat di World Bank]({link_resmi})")

# =============================================================================
# 4. PENARIKAN DATA INDONESIA — 100% LIVE
# =============================================================================
st.subheader("2. Penarikan Data Indonesia")

if st.button("📊 Ambil Data Indonesia", type="primary"):
    with st.spinner(f"Mengunduh data untuk '{selected_ind['name']}'..."):
        data_url = (
            f"https://api.worldbank.org/v2/country/IDN/indicator/{kode_indikator}"
            f"?format=json&per_page=1000"
        )
        try:
            r_data = requests.get(data_url, headers=HEADERS, timeout=20)

            if r_data.status_code != 200:
                st.error(f"Gagal menghubungi server World Bank (HTTP {r_data.status_code}).")
                st.stop()

            data_json = r_data.json()
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
            if "% of gdp" in name_lower:
                unit = "% of GDP"
            elif "current us$" in name_lower or "(current" in name_lower:
                unit = "USD"
            elif "constant" in name_lower and ("lcu" in name_lower or "us$" in name_lower):
                unit = "Constant USD"
            elif "per capita" in name_lower and "us$" in name_lower:
                unit = "USD per Capita"
            elif "%" in selected_ind["name"]:
                unit = "%"
            elif any(k in name_lower for k in ["number", "count", "total", "persons", "people"]):
                unit = "Jiwa"
            elif "index" in name_lower:
                unit = "Index"
            elif "ratio" in name_lower:
                unit = "Rasio"
            else:
                unit = "Nilai"

            val_col = f"Nilai ({unit})"
            df = (
                pd.DataFrame(records)
                .groupby("Tahun", as_index=False)["nilai_raw"]
                .mean()
                .round(2)
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
                f"{kode_indikator}_indonesia.csv",
                "text/csv"
            )
            buffer = io.BytesIO()
            with pd.ExcelWriter(buffer, engine="openpyxl") as writer:
                df.to_excel(writer, index=False, sheet_name="World Bank Data")
            col2.download_button(
                "📊 Unduh Excel (.xlsx)",
                buffer.getvalue(),
                f"{kode_indikator}_indonesia.xlsx",
                "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            )

            # Visualisasi Plotly
            fig = go.Figure()
            fig.add_trace(go.Scatter(
                x=df["Tahun"],
                y=df[val_col],
                mode="lines+markers",
                name="Indonesia (World Bank)",
                line=dict(width=2.5, color="#009688"),
                marker=dict(size=7),
                hovertemplate=f"Tahun %{{x}}<br>Nilai: %{{y:,.2f}} {unit}<extra></extra>"
            ))
            fig.update_layout(
                xaxis=dict(title="Tahun", tickmode="linear"),
                yaxis=dict(title=unit),
                hovermode="x unified",
                margin=dict(l=20, r=20, t=30, b=20)
            )
            st.plotly_chart(fig, use_container_width=True)

            with st.expander("📋 Tabel Angka Lengkap"):
                st.dataframe(
                    df.sort_values(by="Tahun", ascending=False),
                    use_container_width=True
                )

        except Exception as e:
            st.error(f"Gagal mengambil data dari server World Bank: {e}")
